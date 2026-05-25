"""Shared policy logic for Data Engineering Cursor hooks (stdlib only)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from lib_hook_io import (
    exit_allow_pre_tool,
    exit_ask_pre_tool,
    exit_block_pre_tool,
    exit_post_additional_context,
    exit_post_empty,
    exit_shell_allow,
    exit_shell_ask,
    exit_shell_deny,
    exit_subagent_followup,
    read_stdin_json,
    write_stdout_json,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POLICIES_DIR = Path(__file__).resolve().parent / "policies"
ORCH_DIR = REPO_ROOT / ".cursor" / "orchestration"
LOCKS_PATH = ORCH_DIR / "locks.json"
LAST_STORY_PATH = ORCH_DIR / "last_story.json"


def _load_json(name: str) -> dict[str, Any]:
    path = POLICIES_DIR / name
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def get_tool_name(data: dict[str, Any]) -> str:
    for key in ("tool_name", "tool", "toolName", "tool_name", "name"):
        val = data.get(key)
        if val:
            return str(val)
    return ""


def get_tool_input(data: dict[str, Any]) -> dict[str, Any]:
    ti = data.get("tool_input")
    if isinstance(ti, dict):
        return ti
    inn = data.get("input")
    if isinstance(inn, dict):
        return inn
    return {}


def get_shell_command(data: dict[str, Any]) -> str:
    ti = get_tool_input(data)
    for path in (ti.get("command"), data.get("command"), data.get("shell_command")):
        if path:
            return str(path)
    return ""


def get_write_path(data: dict[str, Any]) -> str:
    ti = get_tool_input(data)
    for path in (ti.get("path"), ti.get("file_path"), data.get("path")):
        if path:
            return str(path)
    return ""


def get_write_contents(data: dict[str, Any]) -> str:
    ti = get_tool_input(data)
    for path in (ti.get("contents"), ti.get("content"), data.get("contents"), data.get("content")):
        if path is not None:
            return str(path)
    return ""


def get_task_text(data: dict[str, Any]) -> str:
    ti = get_tool_input(data)
    for path in (ti.get("prompt"), ti.get("task"), data.get("prompt"), data.get("task")):
        if path:
            return str(path)
    return json.dumps(data, ensure_ascii=False)


def normalize_subagent_slug(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = s.replace("_", "-")
    return s


def get_task_subagent_type(data: dict[str, Any]) -> str | None:
    """Resolve worker subagent type from Task payload (tool_input, top-level, or prompt hints)."""
    ti = get_tool_input(data)
    for key in (
        "subagent_type",
        "subagentType",
        "agent_type",
        "agentType",
        "worker",
        "worker_type",
        "workerType",
    ):
        for container in (ti, data):
            v = container.get(key)
            if isinstance(v, str) and v.strip():
                return normalize_subagent_slug(v)
    prompt = get_task_text(data)
    for pat in (
        r"subagent_type\s*[:=]\s*[\"']?([A-Za-z0-9_.-]+)",
        r"subagentType\s*[:=]\s*[\"']?([A-Za-z0-9_.-]+)",
    ):
        m = re.search(pat, prompt, re.I)
        if m:
            return normalize_subagent_slug(m.group(1))
    return None


def orchestration_agent_mode_sets() -> tuple[set[str], set[str]]:
    raw = _load_json("orchestration_agents.json")
    planning: set[str] = set()
    impl: set[str] = set()
    for x in raw.get("planning_subagent_types", []) if isinstance(raw.get("planning_subagent_types"), list) else []:
        if isinstance(x, str) and x.strip():
            planning.add(normalize_subagent_slug(x))
    for x in raw.get("implementation_subagent_types", []) if isinstance(
        raw.get("implementation_subagent_types"), list
    ) else []:
        if isinstance(x, str) and x.strip():
            impl.add(normalize_subagent_slug(x))
    return planning, impl


def is_planning_task_subagent(subagent_type: str | None) -> bool:
    if not subagent_type:
        return False
    planning, _impl = orchestration_agent_mode_sets()
    return normalize_subagent_slug(subagent_type) in planning


def task_implementation_gates_required(subagent_type: str | None) -> bool:
    """Planning agents skip Jira + OWNERSHIP; implementation and unknown agents require both."""
    if subagent_type and is_planning_task_subagent(subagent_type):
        return False
    return True


def orchestration_task_violation(data: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return (user_message, agent_message) if Task orchestration should block; else (None, None)."""
    if get_tool_name(data) != "Task":
        return None, None
    sub = get_task_subagent_type(data)
    if not task_implementation_gates_required(sub):
        return None, None
    prompt = get_task_text(data)
    keys = list(dict.fromkeys(filter_keys(jira_keys(prompt))))
    if len(keys) != 1:
        return (
            "Orchestration (implementation Task): include exactly one Jira story key "
            f"(allowed projects: {', '.join(sorted(allowed_jira_projects()))}). "
            "Planning agents (technical-planning-agent, orchestrator-agent, qa-agent, security-agent, "
            "documentation-agent) may omit keys; set subagent_type on Task for planning mode.",
            f"Found keys: {keys}; subagent_type={sub!r}",
        )
    if "OWNERSHIP=" not in prompt.upper():
        return (
            "Orchestration (implementation Task): include OWNERSHIP=path/prefix/ in the Task prompt "
            "(isolated code ownership). Planning/orchestration agents may omit OWNERSHIP.",
            None,
        )
    return None, None


def get_post_tool_output_text(data: dict[str, Any]) -> str:
    for key in ("tool_output", "output", "result", "content"):
        val = data.get(key)
        if val is not None:
            return str(val)
    return json.dumps(data, ensure_ascii=False)


def scan_secrets_and_unsafe(text: str) -> list[str]:
    reasons: list[str] = []
    policies = _load_json("secret_regex.json")
    for item in policies.get("block_regex", []) if isinstance(policies.get("block_regex"), list) else []:
        if not isinstance(item, dict):
            continue
        pat, msg = item.get("pattern"), item.get("message", "blocked pattern")
        if not isinstance(pat, str) or not isinstance(msg, str):
            continue
        try:
            if re.search(pat, text, re.IGNORECASE | re.MULTILINE):
                reasons.append(msg)
        except re.error:
            continue
    destructive = _load_json("destructive_shell_regex.json")
    for pat in destructive.get("block_command_regex", []) if isinstance(
        destructive.get("block_command_regex"), list
    ) else []:
        if not isinstance(pat, str):
            continue
        try:
            if re.search(pat, text, re.IGNORECASE):
                reasons.append(f"destructive or unsafe shell pattern: {pat}")
        except re.error:
            continue
    return reasons


def is_pipeline_path(rel: str) -> bool:
    p = rel.replace("\\", "/").lower()
    if not p.endswith((".py", ".ipynb")):
        return False
    return bool(
        re.search(r"(^|/)(pipelines?|databricks|src|packages)(/|$)", p, re.IGNORECASE)
    )


def is_silver_or_gold_path(rel: str) -> bool:
    p = rel.replace("\\", "/").lower()
    return "/silver/" in p or "/gold/" in p or p.endswith("/silver") or p.endswith("/gold")


def scan_spark_antipatterns(rel_path: str, content: str) -> list[str]:
    if not content or not is_pipeline_path(rel_path):
        return []
    pol = _load_json("spark_rules.json")
    reasons: list[str] = []
    for rule in pol.get("rules", []) if isinstance(pol.get("rules"), list) else []:
        if not isinstance(rule, dict):
            continue
        pat, msg = rule.get("pattern"), rule.get("message", "spark policy")
        if not isinstance(pat, str) or not isinstance(msg, str):
            continue
        if rule.get("path_must_match_silver_gold") and not is_silver_or_gold_path(rel_path):
            continue
        try:
            if re.search(pat, content, re.MULTILINE):
                reasons.append(msg)
        except re.error:
            continue
    for pat, msg, allow_token in (
        (r"\.collect\(\)", "Avoid driver-side .collect(); use '# hooks:allow-collect' if intentional.", "hooks:allow-collect"),
        (
            r"\.toPandas\(\)",
            "Avoid unbounded .toPandas(); use '# hooks:allow-topandas' if intentional.",
            "hooks:allow-topandas",
        ),
    ):
        for m in re.finditer(pat, content):
            start = max(0, m.start() - 200)
            snippet = content[start : m.end() + 1]
            if allow_token in snippet:
                continue
            reasons.append(msg)
            break
    if is_silver_or_gold_path(rel_path):
        if re.search(r"\.write\(", content) and "partitionBy" not in content:
            if "# hooks:ignore-partition" not in content:
                reasons.append(
                    "Silver/gold write without partitionBy(); add partitioning or "
                    "'# hooks:ignore-partition' with justification."
                )
    return reasons


def jira_keys(text: str) -> list[str]:
    return re.findall(r"\b[A-Z][A-Z0-9]+-\d+\b", text)


def allowed_jira_projects() -> set[str]:
    raw = os.environ.get("DE_HOOK_JIRA_PROJECTS", "PROJ,JIRA,DE")
    return {p.strip().upper() for p in raw.split(",") if p.strip()}


def filter_keys(keys: list[str]) -> list[str]:
    allow = allowed_jira_projects()
    filtered = [k for k in keys if k.split("-")[0].upper() in allow]
    return filtered or keys


def hook_owner() -> str:
    return os.environ.get("DE_HOOK_OWNER") or os.environ.get("USER", "unknown")


def current_git_branch() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        return (proc.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def pipeline_root_key(rel_path: str) -> str | None:
    parts = Path(rel_path).as_posix().strip("/").split("/")
    lower = [p.lower() for p in parts]
    try:
        idx = lower.index("pipelines")
    except ValueError:
        return None
    if len(parts) <= idx + 1:
        return None
    return "/".join(parts[: idx + 2])


def load_locks() -> dict[str, Any]:
    if not LOCKS_PATH.is_file():
        return {"version": 1, "locks": []}
    try:
        with LOCKS_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {"version": 1, "locks": []}
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "locks": []}


def save_locks(doc: dict[str, Any]) -> None:
    ORCH_DIR.mkdir(parents=True, exist_ok=True)
    tmp = LOCKS_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    tmp.replace(LOCKS_PATH)


def ensure_lock_for_write(rel_path: str) -> str | None:
    root = pipeline_root_key(rel_path)
    if root is None:
        return None
    branch = current_git_branch()
    owner = hook_owner()
    doc = load_locks()
    locks = doc.get("locks")
    if not isinstance(locks, list):
        locks = []
    for entry in locks:
        if not isinstance(entry, dict):
            continue
        if entry.get("root") == root and entry.get("branch") not in (branch, None, ""):
            return (
                f"Pipeline root '{root}' is locked by branch '{entry.get('branch')}' "
                f"(owner={entry.get('owner')}). Coordinate or clear locks.json."
            )
    found = False
    for entry in locks:
        if isinstance(entry, dict) and entry.get("root") == root and entry.get("branch") == branch:
            entry["owner"] = owner
            found = True
            break
    if not found:
        locks.append({"root": root, "branch": branch, "owner": owner, "ticket": ""})
    doc["locks"] = locks
    save_locks(doc)
    return None


def deploy_policy() -> dict[str, Any]:
    return _load_json("databricks_env.json")


def analyze_databricks_shell(command: str) -> tuple[str | None, str | None]:
    cmd = command.strip()
    pol = deploy_policy()
    risky = bool(
        re.search(r"(databricks|dbx)\s+bundle\s+(deploy|run|destroy)", cmd, re.IGNORECASE)
        or re.search(r"\b(terraform|pulumi)\s+(apply|destroy|up)\b", cmd, re.IGNORECASE)
    )
    if not risky:
        return None, None

    allow_envs = pol.get("allow_bundle_env_values", ["dev", "staging"])
    if not isinstance(allow_envs, list):
        allow_envs = ["dev", "staging"]

    env = (os.environ.get("DATABRICKS_BUNDLE_ENV") or "").strip().lower()
    if not env:
        return (
            "Set DATABRICKS_BUNDLE_ENV to an allowed value before deploy-style commands. "
            f"Allowed: {', '.join(allow_envs)}.",
            None,
        )
    if env not in {str(x).lower() for x in allow_envs}:
        approved = (os.environ.get("DEPLOY_APPROVED_REF") or "").strip()
        if env == "prod" and len(approved) >= 7:
            return None, None
        if env == "prod":
            return (
                "Production deploy/run is blocked locally unless DEPLOY_APPROVED_REF is set "
                "to an approved git SHA (typically injected by CI after merge).",
                None,
            )
        return (f"DATABRICKS_BUNDLE_ENV='{env}' is not in the allowlist for local deploys.", None)

    if re.search(r"(databricks|dbx)\s+bundle\s+(deploy|run)", cmd, re.IGNORECASE):
        if "bundle validate" not in cmd and not os.environ.get("DE_HOOK_SKIP_BUNDLE_VALIDATE"):
            return (
                "Include `databricks bundle validate` in the same command chain before deploy/run, "
                "or set DE_HOOK_SKIP_BUNDLE_VALIDATE=1 for emergency operations.",
                None,
            )

    if re.search(r"\bterraform\s+apply\b", cmd, re.IGNORECASE):
        if "terraform plan" not in cmd.lower() and not os.environ.get("DE_HOOK_SKIP_IAC_PLAN"):
            return (
                "Include `terraform plan` in the same command chain before `terraform apply`, "
                "or set DE_HOOK_SKIP_IAC_PLAN=1 for emergency.",
                None,
            )
    if re.search(r"\bpulumi\s+(up|destroy)\b", cmd, re.IGNORECASE):
        if "pulumi preview" not in cmd.lower() and not os.environ.get("DE_HOOK_SKIP_IAC_PLAN"):
            return (
                "Include `pulumi preview` before `pulumi up/destroy`, "
                "or set DE_HOOK_SKIP_IAC_PLAN=1 for emergency.",
                None,
            )

    prod_hosts = pol.get("prod_workspace_host_regex", [])
    if isinstance(prod_hosts, list):
        for pat in prod_hosts:
            if not isinstance(pat, str):
                continue
            try:
                if re.search(pat, cmd, re.IGNORECASE):
                    return ("Command matches prod workspace host policy; blocked.", None)
            except re.error:
                continue

    if re.search(r"bundle\s+run\b", cmd, re.IGNORECASE) and env == "prod":
        return ("bundle run against prod targets is blocked by policy.", None)

    return None, None


def pr_body_from_command(command: str) -> str | None:
    if "--body-file" in command:
        m = re.search(r"--body-file\s+(\S+)", command)
        if m:
            p = Path(m.group(1)).expanduser()
            if not p.is_absolute():
                p = REPO_ROOT / p
            if p.is_file():
                return p.read_text(encoding="utf-8", errors="replace")
    if "--body" in command:
        m = re.search(r"--body\s+(['\"])(.*?)\1", command, re.DOTALL)
        if m:
            return m.group(2)
    return None


def git_changed_files() -> list[str]:
    lines: list[str] = []
    for args in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--name-only", "--cached"],
    ):
        try:
            proc = subprocess.run(
                args,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            lines.extend(ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip())
        except (OSError, subprocess.TimeoutExpired):
            continue
    return sorted(set(lines))


def main_sec_pre_tool() -> None:
    data = read_stdin_json()
    tool = get_tool_name(data)
    ti = get_tool_input(data)
    blob = json.dumps(data, ensure_ascii=False)
    text_parts = [blob]
    if tool in ("Write", "StrReplace"):
        text_parts.append(get_write_contents(data))
    if tool == "Shell" or tool.lower() == "shell":
        text_parts.append(get_shell_command(data))
    if tool.startswith("MCP:") or "MCP" in tool:
        text_parts.append(json.dumps(ti, ensure_ascii=False))
    text = "\n".join(text_parts)
    reasons = scan_secrets_and_unsafe(text)
    if reasons:
        exit_block_pre_tool("Security policy blocked this tool call.", "; ".join(reasons[:6]))
    exit_allow_pre_tool()


def main_spark_pre_tool() -> None:
    """Legacy entrypoint: Spark checks are advisory-only (see `main_spark_post_tool`)."""
    read_stdin_json()
    exit_allow_pre_tool()


def main_spark_post_tool() -> None:
    """After Write/StrReplace: suggest PySpark / pipeline fixes without blocking."""
    data = read_stdin_json()
    path = get_write_path(data)
    if not path:
        exit_post_empty()
    rel = str(Path(path).as_posix())
    if not is_pipeline_path(rel):
        exit_post_empty()

    content = ""
    disk = REPO_ROOT / rel
    if disk.is_file():
        try:
            content = disk.read_text(encoding="utf-8", errors="replace")
        except OSError:
            content = ""
    if not content.strip():
        content = get_write_contents(data) or ""

    reasons = scan_spark_antipatterns(rel, content)
    if reasons:
        exit_post_additional_context(
            "PySpark / pipeline hints (non-blocking):\n- " + "\n- ".join(reasons[:12])
        )
    exit_post_empty()


def main_orch_one_story() -> None:
    data = read_stdin_json()
    tool = get_tool_name(data)
    user_msg, agent_msg = orchestration_task_violation(data)
    if user_msg:
        exit_block_pre_tool(user_msg, agent_msg)
    if tool == "Shell":
        cmd = get_shell_command(data)
        if re.search(r"gh\s+pr\s+(create|edit|ready|merge)\b", cmd) or re.search(
            r"git\s+checkout\s+-b\b", cmd
        ) or re.search(r"\bgit\s+push\b", cmd):
            keys = filter_keys(jira_keys(cmd + " " + current_git_branch()))
            keys = list(dict.fromkeys(keys))
            branch = current_git_branch()
            if branch and branch not in ("main", "master"):
                if not re.match(r"^(feature/)?[A-Z][A-Z0-9]+-\d+(/|-|$)", branch):
                    exit_block_pre_tool(
                        "Branch naming: use feature/PROJ-123-desc or PROJ-123/...",
                        f"Current branch: {branch}",
                    )
            if len(keys) > 1:
                exit_block_pre_tool(
                    "Multiple Jira keys in the same PR/branch command; one story per PR.",
                    str(keys),
                )
    write_stdout_json({"permission": "allow"})
    raise SystemExit(0)


def main_orch_path_lock() -> None:
    data = read_stdin_json()
    tool = get_tool_name(data)
    if tool in ("Write", "StrReplace"):
        rel = get_write_path(data)
        if rel:
            deny = ensure_lock_for_write(rel)
            if deny:
                exit_block_pre_tool(deny, None)
    if tool == "Shell":
        cmd = get_shell_command(data)
        if re.search(r"(databricks|dbx)\s+bundle\s+(deploy|run)\b", cmd, re.IGNORECASE):
            branch = current_git_branch()
            doc = load_locks()
            locks = doc.get("locks") if isinstance(doc.get("locks"), list) else []
            if not any(isinstance(e, dict) and e.get("branch") == branch for e in locks):
                exit_block_pre_tool(
                    "Bundle deploy/run requires a branch lock. Edit a file under pipelines/ first "
                    "or add a locks.json entry for this branch.",
                    None,
                )
    write_stdout_json({"permission": "allow"})
    raise SystemExit(0)


def main_jira_subagent_stop() -> None:
    read_stdin_json()
    if not LAST_STORY_PATH.is_file():
        msg = (
            "Missing `.cursor/orchestration/last_story.json`. Planning/orchestration should "
            "write acceptance_criteria, worker_agent, and dependencies before workers run."
        )
        write_stdout_json({"followup_message": msg})
        raise SystemExit(0)
    try:
        story = json.loads(LAST_STORY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        exit_subagent_followup("last_story.json is invalid JSON; fix before continuing.")

    missing: list[str] = []
    ac = story.get("acceptance_criteria")
    if not (isinstance(ac, str) and ac.strip()):
        missing.append("acceptance_criteria (non-empty string)")
    wa = story.get("worker_agent")
    if not (isinstance(wa, str) and wa.strip()):
        missing.append("worker_agent (e.g. data-engineering-agent)")
    deps = story.get("dependencies")
    ok_deps = (isinstance(deps, list) and len(deps) > 0) or (
        isinstance(deps, str) and deps.strip()
    )
    if not ok_deps:
        missing.append("dependencies (non-empty list or string)")
    if missing:
        exit_subagent_followup(
            "Story artifact incomplete: " + "; ".join(missing) + ". Update last_story.json."
        )
    write_stdout_json({"followup_message": ""})
    raise SystemExit(0)


def main_jira_mcp_post() -> None:
    data = read_stdin_json()
    tool = get_tool_name(data)
    blob = json.dumps(data, ensure_ascii=False)
    if not tool.startswith("MCP:") and not re.search(r"jira|atlassian", tool + blob, re.IGNORECASE):
        exit_post_empty()

    output = get_post_tool_output_text(data)
    checklist: list[str] = []
    if not re.search(r"acceptance|criteria", output, re.IGNORECASE):
        checklist.append("Ensure Jira issue has explicit Acceptance Criteria.")
    if not re.search(r"component|label", output, re.IGNORECASE):
        checklist.append("Add Components/Labels (e.g. agent:data-engineering).")
    if not re.search(r"depend|blocks|is blocked by", output, re.IGNORECASE):
        checklist.append("Link dependencies (Blocks / Is blocked by / Depends on).")
    if checklist:
        exit_post_additional_context("Jira MCP follow-up:\n- " + "\n- ".join(checklist))
    exit_post_empty()


def main_pr_inject() -> None:
    data = read_stdin_json()
    cmd = get_shell_command(data)
    if not re.search(r"gh\s+pr\s+(create|edit)\b", cmd):
        exit_post_empty()
    ctx = (
        "PR checklist (Databricks / DE):\n"
        "- Single Jira story; keep scope aligned.\n"
        "- Tests: pytest (or repo standard) + pipeline tests for touched transforms.\n"
        "- Rollback: prior bundle SHA / job ids / how to revert.\n"
        "- Pipeline impact: inputs, outputs, datasets, blast radius.\n"
    )
    exit_post_additional_context(ctx)


def main_pr_block() -> None:
    data = read_stdin_json()
    cmd = get_shell_command(data)
    if not re.search(r"gh\s+pr\s+(create|ready|merge)\b", cmd):
        write_stdout_json({"permission": "allow"})
        raise SystemExit(0)
    if not shutil.which("gh"):
        exit_block_pre_tool("gh CLI is required for this PR gate; install GitHub CLI.", None)
    body = pr_body_from_command(cmd) or ""
    required = ["## Summary", "## Jira", "## Tests", "## Rollback", "## Pipeline impact"]
    missing = [h for h in required if h.lower() not in body.lower()]
    if missing:
        exit_block_pre_tool(
            "PR body missing sections: " + ", ".join(missing) + ". "
            "Use `--body-file .cursor/tmp/PROJ-123.pr.md` with required headers.",
            None,
        )
    changed = set(git_changed_files())
    pipeline_touched = any(
        re.search(r"(^|/)(pipelines?|databricks)(/|$)", p, re.IGNORECASE) and p.endswith(".py")
        for p in changed
    )
    tests_touched = any(re.search(r"(^|/)tests(/|$)", p) for p in changed) or any(
        "/test_" in p or p.startswith("test_") for p in changed
    )
    if pipeline_touched and not tests_touched:
        exit_block_pre_tool(
            "Pipeline Python changed without test file changes in this branch diff.",
            None,
        )
    write_stdout_json({"permission": "allow"})
    raise SystemExit(0)


def main_pipeline_tests_coach() -> None:
    data = read_stdin_json()
    path = get_write_path(data)
    if not path or not is_pipeline_path(path):
        exit_post_empty()
    changed = set(git_changed_files())
    if not any(Path(p).as_posix().endswith(Path(path).as_posix()) for p in changed):
        exit_post_empty()
    suggestions: list[str] = []
    if not any(re.search(r"(^|/)tests(/|$)", p) for p in changed):
        suggestions.append("Add or update tests under tests/ for transforms and edge cases.")

    def _read_py(rel: str) -> str:
        fp = REPO_ROOT / rel
        if not fp.is_file():
            return ""
        return fp.read_text(encoding="utf-8", errors="ignore")

    schema_hits = any(
        re.search(r"StructType|assertSchemaEqual|json\.loads\(", _read_py(p))
        for p in changed
        if p.endswith(".py")
    )
    if not schema_hits:
        suggestions.append(
            "Add schema assertions (StructType / assertSchemaEqual / explicit JSON schema)."
        )
    if suggestions:
        exit_post_additional_context("Pipeline test coaching:\n- " + "\n- ".join(suggestions))
    exit_post_empty()


def main_dbx_deploy_agent() -> None:
    data = read_stdin_json()
    cmd = get_shell_command(data)
    if not re.search(
        r"(databricks|dbx|terraform|pulumi|\baws\s|\baz\s|\bgcloud\s)", cmd, re.IGNORECASE
    ):
        write_stdout_json({"permission": "allow"})
        raise SystemExit(0)
    deny, ask = analyze_databricks_shell(cmd)
    if deny:
        exit_block_pre_tool(deny, None)
    if ask:
        exit_ask_pre_tool(ask, None)
    reasons = scan_secrets_and_unsafe(cmd)
    if reasons:
        exit_block_pre_tool("Deploy command flagged by secret policy.", "; ".join(reasons[:6]))
    write_stdout_json({"permission": "allow"})
    raise SystemExit(0)


def main_sec_shell_terminal() -> None:
    data = read_stdin_json()
    cmd = str(data.get("command") or data.get("shell_command") or "")
    reasons = scan_secrets_and_unsafe(cmd)
    if reasons:
        exit_shell_deny("Blocked shell command by security policy.", "; ".join(reasons[:6]))
    if re.search(r"curl\s+[^|]*\|\s*(bash|sh)\b", cmd, re.IGNORECASE):
        exit_shell_ask("curl pipes to shell; confirm trust before running.", None)
    exit_shell_allow()


def main_dbx_deploy_terminal() -> None:
    data = read_stdin_json()
    cmd = str(data.get("command") or data.get("shell_command") or "")
    if not re.search(
        r"(databricks|dbx|terraform|pulumi|\baws\s|\baz\s|\bgcloud\s)", cmd, re.IGNORECASE
    ):
        exit_shell_allow()
    deny, ask = analyze_databricks_shell(cmd)
    if deny:
        exit_shell_deny(deny, None)
    if ask:
        exit_shell_ask(ask, None)
    exit_shell_allow()
