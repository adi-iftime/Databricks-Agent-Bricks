"""Pipeline run ingestion tests for SCRUM-135."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mlops_intelligence.ingestion import pipeline_runs as pr  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestRunTransformation(unittest.TestCase):
    def test_run_to_row_success(self) -> None:
        run = _load_fixture("pipeline_runs_page1.json")["runs"][0]
        row = pr.run_to_row(run, ingested_at="2024-05-01 12:00:00")

        self.assertEqual(row["run_id"], "1001")
        self.assertEqual(row["job_id"], "42")
        self.assertEqual(row["status"], "SUCCESS")
        self.assertEqual(row["duration_sec"], 120.0)
        self.assertIsNone(row["cost_usd"])
        self.assertEqual(row["event_ts"], "2024-04-30 18:00:00")
        self.assertEqual(row["ingested_at"], "2024-05-01 12:00:00")

    def test_run_to_row_failed_and_running(self) -> None:
        failed = _load_fixture("pipeline_runs_page1.json")["runs"][1]
        running = _load_fixture("pipeline_runs_page2.json")["runs"][0]

        self.assertEqual(pr.run_to_row(failed, ingested_at="t")["status"], "FAILED")
        self.assertEqual(pr.run_to_row(running, ingested_at="t")["status"], "RUNNING")

    def test_run_to_row_cancelled(self) -> None:
        run = {
            "run_id": 9,
            "job_id": 1,
            "start_time": 1714500000000,
            "state": {"life_cycle_state": "TERMINATED", "result_state": "CANCELED"},
        }
        self.assertEqual(pr.run_to_row(run, ingested_at="t")["status"], "CANCELLED")

    def test_run_to_row_missing_start_time_raises(self) -> None:
        with self.assertRaises(ValueError):
            pr.run_to_row({"run_id": 1, "state": {}}, ingested_at="t")


class TestMergeSql(unittest.TestCase):
    def test_build_merge_sql_keys_on_run_id(self) -> None:
        sql = pr.build_merge_sql("catalog.schema.pipeline_runs")
        self.assertIn("ON target.run_id = source.run_id", sql)
        self.assertIn("WHEN MATCHED THEN UPDATE SET", sql)
        self.assertIn("WHEN NOT MATCHED THEN INSERT", sql)


class TestRetry(unittest.TestCase):
    def test_retry_succeeds_after_transient_failure(self) -> None:
        attempts = {"count": 0}

        def flaky() -> str:
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise urllib_error()
            return "ok"

        with mock.patch("mlops_intelligence.ingestion.pipeline_runs.time.sleep"):
            result = pr.retry_with_backoff(flaky, max_attempts=3, base_delay_sec=0.01)

        self.assertEqual(result, "ok")
        self.assertEqual(attempts["count"], 2)

    def test_retry_stops_on_non_retryable_error(self) -> None:
        def fail() -> None:
            raise ValueError("permanent")

        with self.assertRaises(ValueError):
            pr.retry_with_backoff(fail, max_attempts=3, base_delay_sec=0.01)


def urllib_error() -> Exception:
    import urllib.error

    return urllib.error.HTTPError(
        url="https://example",
        code=503,
        msg="unavailable",
        hdrs=None,
        fp=io.BytesIO(b""),
    )


class TestJobsApiClient(unittest.TestCase):
    def test_list_runs_posts_json_with_auth(self) -> None:
        captured: dict = {}

        def fake_opener(request: object, timeout: float) -> object:
            captured["url"] = request.full_url  # type: ignore[attr-defined]
            captured["data"] = request.data  # type: ignore[attr-defined]
            captured["headers"] = dict(request.header_items())  # type: ignore[attr-defined]
            return io.BytesIO(json.dumps(_load_fixture("pipeline_runs_page1.json")).encode())

        config = pr.JobsApiConfig(
            host="https://dbc.example.com",
            token="test-token",
            max_retries=1,
        )
        client = pr.JobsApiClient(config, opener=fake_opener)
        body = client.list_runs(job_id=42, correlation_id="corr-1")

        self.assertEqual(len(body["runs"]), 2)
        self.assertTrue(body["has_more"])
        self.assertIn("/api/2.1/jobs/runs/list", captured["url"])
        payload = json.loads(captured["data"].decode())
        self.assertEqual(payload["job_id"], 42)
        self.assertEqual(payload["limit"], 25)
        self.assertEqual(captured["headers"]["Authorization"], "Bearer test-token")


class TestPagination(unittest.TestCase):
    def test_paginate_runs_yields_all_pages(self) -> None:
        pages = [
            _load_fixture("pipeline_runs_page1.json"),
            _load_fixture("pipeline_runs_page2.json"),
        ]
        calls: list[str | None] = []

        class StubClient:
            def list_runs(
                self,
                *,
                job_id: int | None,
                page_token: str | None,
                correlation_id: str,
            ) -> dict:
                calls.append(page_token)
                if page_token is None:
                    return pages[0]
                return pages[1]

        collected = list(
            pr.paginate_runs(StubClient(), job_id=None, correlation_id="corr-paginate")
        )
        self.assertEqual(calls, [None, "token-page-2"], "expected two paginated API calls")
        self.assertEqual(len(collected), 2)
        self.assertEqual(len(collected[0]), 2)
        self.assertEqual(len(collected[1]), 1)


class TestMergePipelineRuns(unittest.TestCase):
    def test_merge_pipeline_runs_executes_merge_sql(self) -> None:
        spark = mock.MagicMock()
        df = mock.MagicMock()
        spark.createDataFrame.return_value = df

        rows = pr.runs_to_rows(
            _load_fixture("pipeline_runs_page1.json")["runs"],
            ingested_at="2024-05-01 12:00:00",
        )
        count = pr.merge_pipeline_runs(
            spark,
            rows,
            target_table="test.catalog.pipeline_runs",
            correlation_id="corr-merge",
        )

        self.assertEqual(count, 2)
        spark.createDataFrame.assert_called_once_with(rows)
        df.createOrReplaceTempView.assert_called_once_with(pr.STAGING_VIEW)
        merge_sql = spark.sql.call_args[0][0]
        self.assertIn("test.catalog.pipeline_runs", merge_sql)
        self.assertIn("ON target.run_id = source.run_id", merge_sql)

    def test_merge_pipeline_runs_idempotent_sql_updates_existing(self) -> None:
        sql = pr.build_merge_sql("catalog.schema.pipeline_runs")
        self.assertIn("WHEN MATCHED THEN UPDATE SET", sql)
        self.assertIn("job_id = source.job_id", sql)

    def test_merge_empty_rows_skips_spark(self) -> None:
        spark = mock.MagicMock()
        self.assertEqual(
            pr.merge_pipeline_runs(spark, [], correlation_id="corr-empty"),
            0,
        )
        spark.createDataFrame.assert_not_called()


class TestIngestPipelineRuns(unittest.TestCase):
    def test_ingest_pipeline_runs_end_to_end_with_stub_client(self) -> None:
        page1 = _load_fixture("pipeline_runs_page1.json")
        page2 = _load_fixture("pipeline_runs_page2.json")

        class StubClient:
            def list_runs(
                self,
                *,
                job_id: int | None,
                page_token: str | None,
                correlation_id: str,
            ) -> dict:
                if page_token is None:
                    return page1
                return page2

        spark = mock.MagicMock()
        df = mock.MagicMock()
        spark.createDataFrame.return_value = df

        total = pr.ingest_pipeline_runs(
            spark,
            client=StubClient(),
            target_table="test.catalog.pipeline_runs",
            correlation_id="corr-ingest",
        )

        self.assertEqual(total, 3)
        self.assertEqual(spark.sql.call_count, 2)

    def test_ingest_twice_same_rows_is_idempotent_by_merge(self) -> None:
        runs = _load_fixture("pipeline_runs_page1.json")["runs"]
        rows = pr.runs_to_rows(runs, ingested_at="2024-05-01 12:00:00")
        spark = mock.MagicMock()
        df = mock.MagicMock()
        spark.createDataFrame.return_value = df

        pr.merge_pipeline_runs(spark, rows, target_table="t", correlation_id="c1")
        pr.merge_pipeline_runs(spark, rows, target_table="t", correlation_id="c2")

        for call in spark.sql.call_args_list:
            self.assertIn("ON target.run_id = source.run_id", call[0][0])


class TestStructuredLogging(unittest.TestCase):
    def test_correlation_logger_attaches_extra(self) -> None:
        adapter = pr.correlation_logger("corr-log")
        with self.assertLogs(pr.logger, level="INFO") as captured:
            adapter.info("ingestion checkpoint")

        self.assertIn("ingestion checkpoint", captured.output[0])


class TestJobsApiConfig(unittest.TestCase):
    def test_from_env_requires_host(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                pr.JobsApiConfig.from_env()

    def test_from_env_reads_variables(self) -> None:
        env = {
            "DATABRICKS_HOST": "https://dbc.example.com/",
            "DATABRICKS_TOKEN": "token",
            "DATABRICKS_API_TIMEOUT_SEC": "45",
            "DATABRICKS_API_MAX_RETRIES": "5",
            "DATABRICKS_API_PAGE_SIZE": "50",
        }
        with mock.patch.dict("os.environ", env, clear=True):
            config = pr.JobsApiConfig.from_env()

        self.assertEqual(config.host, "https://dbc.example.com")
        self.assertEqual(config.token, "token")
        self.assertEqual(config.timeout_sec, 45.0)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.page_size, 50)


if __name__ == "__main__":
    unittest.main()
