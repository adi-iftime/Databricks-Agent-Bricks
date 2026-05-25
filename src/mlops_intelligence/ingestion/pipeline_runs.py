"""Pipeline run telemetry ingestion from the Databricks Jobs API into Delta."""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Iterator, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

PIPELINE_RUN_COLUMNS = (
    "run_id",
    "job_id",
    "status",
    "duration_sec",
    "cost_usd",
    "event_ts",
    "ingested_at",
)

STAGING_VIEW = "pipeline_runs_staging"
DEFAULT_TARGET_TABLE = "mlops_intelligence_dev.bronze_ops.pipeline_runs"
RUNS_LIST_PATH = "/api/2.1/jobs/runs/list"

_RETRYABLE_HTTP_CODES = frozenset({429, 500, 502, 503, 504})


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _ms_to_timestamp(ms: int | float | None) -> str | None:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def correlation_logger(correlation_id: str) -> logging.LoggerAdapter:
    """Return a logger adapter that attaches correlation_id to every record."""
    return logging.LoggerAdapter(
        logger,
        {
            "correlation_id": correlation_id,
        },
    )


def normalize_status(state: dict[str, Any] | None) -> str:
    """Map Databricks run state to pipeline_runs.status contract values."""
    if not state:
        return "FAILED"

    life = (state.get("life_cycle_state") or "").upper()
    result = (state.get("result_state") or "").upper()

    if life in {"RUNNING", "PENDING", "BLOCKED", "WAITING_FOR_RETRY"}:
        return "RUNNING"
    if result == "SUCCESS":
        return "SUCCESS"
    if result in {"FAILED", "TIMEDOUT"}:
        return "FAILED"
    if result == "CANCELED" or life == "SKIPPED":
        return "CANCELLED"
    if life == "TERMINATED":
        return "FAILED"
    return "FAILED"


def run_to_row(run: dict[str, Any], *, ingested_at: str | None = None) -> dict[str, Any]:
    """Transform a Databricks Jobs API run object into a pipeline_runs row."""
    state = run.get("state") or {}
    start_ms = run.get("start_time")
    end_ms = run.get("end_time")
    run_duration_ms = run.get("run_duration")

    duration_sec: float | None = None
    if run_duration_ms is not None:
        duration_sec = float(run_duration_ms) / 1000.0
    elif start_ms is not None and end_ms is not None:
        duration_sec = max(0.0, (float(end_ms) - float(start_ms)) / 1000.0)

    cost_usd = run.get("cost_usd")
    if cost_usd is not None:
        cost_usd = float(cost_usd)

    event_ts = _ms_to_timestamp(start_ms)
    if event_ts is None:
        raise ValueError(f"run {run.get('run_id')} missing start_time")

    return {
        "run_id": str(run["run_id"]),
        "job_id": str(run["job_id"]) if run.get("job_id") is not None else None,
        "status": normalize_status(state),
        "duration_sec": duration_sec,
        "cost_usd": cost_usd,
        "event_ts": event_ts,
        "ingested_at": ingested_at or _utc_now_iso(),
    }


def runs_to_rows(runs: list[dict[str, Any]], *, ingested_at: str | None = None) -> list[dict[str, Any]]:
    return [run_to_row(run, ingested_at=ingested_at) for run in runs]


def build_merge_sql(target_table: str, staging_view: str = STAGING_VIEW) -> str:
    """Build idempotent MERGE keyed on run_id."""
    return f"""
MERGE INTO {target_table} AS target
USING {staging_view} AS source
ON target.run_id = source.run_id
WHEN MATCHED THEN UPDATE SET
  job_id = source.job_id,
  status = source.status,
  duration_sec = source.duration_sec,
  cost_usd = source.cost_usd,
  event_ts = source.event_ts,
  ingested_at = source.ingested_at
WHEN NOT MATCHED THEN INSERT (
  run_id, job_id, status, duration_sec, cost_usd, event_ts, ingested_at
) VALUES (
  source.run_id, source.job_id, source.status, source.duration_sec,
  source.cost_usd, source.event_ts, source.ingested_at
)
""".strip()


def retry_with_backoff(
    operation: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay_sec: float = 1.0,
    retryable: Callable[[Exception], bool] | None = None,
    log: logging.LoggerAdapter | logging.Logger | None = None,
) -> T:
    """Execute operation with exponential backoff on retryable failures."""
    if retryable is None:
        retryable = _is_retryable_exception

    attempt = 0
    while True:
        attempt += 1
        try:
            return operation()
        except Exception as exc:
            if attempt >= max_attempts or not retryable(exc):
                raise
            delay = base_delay_sec * (2 ** (attempt - 1))
            if log is not None:
                log.warning(
                    "retrying after failure attempt=%s delay_sec=%s error=%s",
                    attempt,
                    delay,
                    exc,
                )
            time.sleep(delay)


def _is_retryable_exception(exc: Exception) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in _RETRYABLE_HTTP_CODES
    if isinstance(exc, urllib.error.URLError):
        return True
    return False


@dataclass(frozen=True)
class JobsApiConfig:
    host: str
    token: str | None = None
    timeout_sec: float = 30.0
    max_retries: int = 3
    page_size: int = 25

    @classmethod
    def from_env(cls) -> JobsApiConfig:
        host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
        if not host:
            raise ValueError("DATABRICKS_HOST environment variable is required")
        return cls(
            host=host,
            token=os.environ.get("DATABRICKS_TOKEN"),
            timeout_sec=float(os.environ.get("DATABRICKS_API_TIMEOUT_SEC", "30")),
            max_retries=int(os.environ.get("DATABRICKS_API_MAX_RETRIES", "3")),
            page_size=int(os.environ.get("DATABRICKS_API_PAGE_SIZE", "25")),
        )


class JobsApiClient:
    """Minimal Databricks Jobs API client with pagination and retries."""

    def __init__(
        self,
        config: JobsApiConfig,
        *,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        self._config = config
        self._opener = opener or urllib.request.urlopen

    def list_runs(
        self,
        *,
        job_id: int | None = None,
        page_token: str | None = None,
        correlation_id: str,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "limit": self._config.page_size,
            "expand_tasks": False,
        }
        if job_id is not None:
            payload["job_id"] = job_id
        if page_token:
            payload["page_token"] = page_token

        log = correlation_logger(correlation_id)
        return retry_with_backoff(
            lambda: self._post_json(RUNS_LIST_PATH, payload),
            max_attempts=self._config.max_retries,
            log=log,
        )

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._config.host}{path}"
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._config.token:
            headers["Authorization"] = f"Bearer {self._config.token}"

        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with self._opener(request, timeout=self._config.timeout_sec) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw)


def paginate_runs(
    client: JobsApiClient,
    *,
    job_id: int | None = None,
    correlation_id: str,
) -> Iterator[list[dict[str, Any]]]:
    """Yield each page of run objects from the Jobs API."""
    page_token: str | None = None
    log = correlation_logger(correlation_id)

    while True:
        page = client.list_runs(
            job_id=job_id,
            page_token=page_token,
            correlation_id=correlation_id,
        )
        runs = page.get("runs") or []
        log.info(
            "fetched runs page run_count=%s has_more=%s",
            len(runs),
            page.get("has_more"),
        )
        if runs:
            yield runs

        if not page.get("has_more"):
            break
        page_token = page.get("next_page_token")
        if not page_token:
            break


def merge_pipeline_runs(
    spark: Any,
    rows: list[dict[str, Any]],
    *,
    target_table: str = DEFAULT_TARGET_TABLE,
    correlation_id: str,
) -> int:
    """MERGE rows into pipeline_runs by run_id; returns rows staged."""
    log = correlation_logger(correlation_id)
    if not rows:
        log.info("no pipeline runs to merge")
        return 0

    df = spark.createDataFrame(rows)
    df.createOrReplaceTempView(STAGING_VIEW)
    merge_sql = build_merge_sql(target_table)
    log.info("merging pipeline runs row_count=%s target_table=%s", len(rows), target_table)
    spark.sql(merge_sql)
    return len(rows)


def ingest_pipeline_runs(
    spark: Any,
    *,
    client: JobsApiClient | None = None,
    job_id: int | None = None,
    target_table: str | None = None,
    correlation_id: str | None = None,
) -> int:
    """Fetch Databricks job runs and MERGE them into pipeline_runs."""
    corr_id = correlation_id or str(uuid.uuid4())
    log = correlation_logger(corr_id)
    table = target_table or os.environ.get("PIPELINE_RUNS_TABLE", DEFAULT_TARGET_TABLE)

    api_client = client or JobsApiClient(JobsApiConfig.from_env())
    ingested_at = _utc_now_iso()
    total = 0

    log.info(
        "starting pipeline run ingestion job_id=%s target_table=%s",
        job_id,
        table,
    )

    for page in paginate_runs(api_client, job_id=job_id, correlation_id=corr_id):
        rows = runs_to_rows(page, ingested_at=ingested_at)
        total += merge_pipeline_runs(
            spark,
            rows,
            target_table=table,
            correlation_id=corr_id,
        )

    log.info("completed pipeline run ingestion merged_rows=%s", total)
    return total
