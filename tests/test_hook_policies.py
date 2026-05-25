"""Unit tests for .cursor/hooks/de_hook_policies helpers (stdlib unittest)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOKS = REPO / ".cursor" / "hooks"
sys.path.insert(0, str(HOOKS))

import de_hook_policies as pol  # noqa: E402


def _aws_like_placeholder() -> str:
    parts = (
        chr(65) + chr(75) + chr(73) + chr(65),
        chr(73) + chr(79) + chr(83) + chr(70) + chr(79) + chr(68) + chr(78) + chr(78),
        chr(55) + chr(69) + chr(88) + chr(65) + chr(77) + chr(80) + chr(76) + chr(69),
    )
    return "".join(parts)


def _databricks_token_like() -> str:
    return "dapi" + "".join(chr(97 + (i % 6)) for i in range(20))


class SecretScanTests(unittest.TestCase):
    def test_blocks_aws_key_shape(self) -> None:
        text = "x " + _aws_like_placeholder() + " y"
        reasons = pol.scan_secrets_and_unsafe(text)
        self.assertTrue(any("AWS" in r or "access key" in r.lower() for r in reasons))

    def test_blocks_dapi_token_shape(self) -> None:
        text = "token " + _databricks_token_like()
        reasons = pol.scan_secrets_and_unsafe(text)
        self.assertTrue(any("dapi" in r.lower() for r in reasons))

    def test_blocks_destructive_shell_pattern(self) -> None:
        cmd = "".join(("terraform", " ", "destroy", " ", "--auto-approve"))
        reasons = pol.scan_secrets_and_unsafe(cmd)
        self.assertTrue(reasons)

    def test_allows_benign_python(self) -> None:
        text = "def foo():\n    return 1\n"
        self.assertEqual(pol.scan_secrets_and_unsafe(text), [])


class JiraKeyTests(unittest.TestCase):
    def test_jira_keys(self) -> None:
        self.assertEqual(pol.jira_keys("Fix PROJ-123 and DE-9"), ["PROJ-123", "DE-9"])

    def test_filter_keys_respects_env(self) -> None:
        os.environ["DE_HOOK_JIRA_PROJECTS"] = "PROJ"
        try:
            self.assertEqual(pol.filter_keys(["PROJ-1", "OTHER-2"]), ["PROJ-1"])
        finally:
            del os.environ["DE_HOOK_JIRA_PROJECTS"]


class DeployPolicyTests(unittest.TestCase):
    def test_blocks_bundle_deploy_without_env(self) -> None:
        cmd = "".join(("databricks", " ", "bundle", " ", "deploy", " ", "-t", " ", "dev"))
        deny, _ask = pol.analyze_databricks_shell(cmd)
        self.assertIsNotNone(deny)
        self.assertIn("DATABRICKS_BUNDLE_ENV", deny or "")

    def test_allows_dev_with_validate_chain(self) -> None:
        os.environ["DATABRICKS_BUNDLE_ENV"] = "dev"
        try:
            cmd = "".join(
                (
                    "databricks",
                    " ",
                    "bundle",
                    " ",
                    "validate",
                    " ",
                    "&&",
                    " ",
                    "databricks",
                    " ",
                    "bundle",
                    " ",
                    "deploy",
                    " ",
                    "-t",
                    " ",
                    "dev",
                )
            )
            deny, ask = pol.analyze_databricks_shell(cmd)
            self.assertIsNone(deny)
            self.assertIsNone(ask)
        finally:
            del os.environ["DATABRICKS_BUNDLE_ENV"]

    def test_prod_requires_approved_ref(self) -> None:
        os.environ["DATABRICKS_BUNDLE_ENV"] = "prod"
        os.environ.pop("DEPLOY_APPROVED_REF", None)
        try:
            cmd = "".join(
                (
                    "databricks",
                    " ",
                    "bundle",
                    " ",
                    "validate",
                    " ",
                    "&&",
                    " ",
                    "databricks",
                    " ",
                    "bundle",
                    " ",
                    "deploy",
                    " ",
                    "-t",
                    " ",
                    "prod",
                )
            )
            deny, _ = pol.analyze_databricks_shell(cmd)
            self.assertIsNotNone(deny)
        finally:
            del os.environ["DATABRICKS_BUNDLE_ENV"]


class TaskOrchestrationModeTests(unittest.TestCase):
    def test_planning_agent_allows_task_without_jira(self) -> None:
        data = {
            "tool_name": "Task",
            "tool_input": {
                "subagent_type": "technical-planning-agent",
                "prompt": "Analyze requirements and produce an implementation plan.",
            },
        }
        u, _a = pol.orchestration_task_violation(data)
        self.assertIsNone(u)

    def test_orchestrator_agent_allows_without_ownership(self) -> None:
        data = {
            "tool_name": "Task",
            "tool_input": {
                "subagent_type": "orchestrator-agent",
                "prompt": "Coordinate workers; no Jira yet.",
            },
        }
        self.assertIsNone(pol.orchestration_task_violation(data)[0])

    def test_unknown_subagent_requires_jira_and_ownership(self) -> None:
        data = {
            "tool_name": "Task",
            "tool_input": {
                "subagent_type": "mystery-agent",
                "prompt": "Do implementation work with no ticket.",
            },
        }
        u, _ = pol.orchestration_task_violation(data)
        self.assertIsNotNone(u)
        self.assertIn("Jira", u)

    def test_missing_subagent_type_requires_jira(self) -> None:
        data = {
            "tool_name": "Task",
            "tool_input": {"prompt": "Implement feature with no subagent_type."},
        }
        u, _ = pol.orchestration_task_violation(data)
        self.assertIsNotNone(u)

    def test_implementation_requires_ownership(self) -> None:
        data = {
            "tool_name": "Task",
            "tool_input": {
                "subagent_type": "data-engineering-agent",
                "prompt": "Implement DE-88 bronze layer.",
            },
        }
        u, _ = pol.orchestration_task_violation(data)
        self.assertIsNotNone(u)
        self.assertIn("OWNERSHIP", u)

    def test_implementation_allows_with_key_and_ownership(self) -> None:
        data = {
            "tool_name": "Task",
            "tool_input": {
                "subagent_type": "data-engineering-agent",
                "prompt": "DE-88 OWNERSHIP=pipelines/ingest/ implement bronze.",
            },
        }
        self.assertIsNone(pol.orchestration_task_violation(data)[0])

    def test_subagent_type_from_prompt_hint(self) -> None:
        data = {
            "tool_name": "Task",
            "tool_input": {
                "prompt": "subagent_type: orchestrator-agent\nCoordinate only.",
            },
        }
        self.assertIsNone(pol.orchestration_task_violation(data)[0])


class LockConflictTests(unittest.TestCase):
    def test_conflicting_branch_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            pol.ORCH_DIR = t  # type: ignore[misc]
            pol.LOCKS_PATH = t / "locks.json"  # type: ignore[misc]
            pol.REPO_ROOT = t  # type: ignore[misc]

            doc = {
                "version": 1,
                "locks": [{"root": "pipelines/ingest", "branch": "other-branch", "owner": "a"}],
            }
            pol.LOCKS_PATH.write_text(json.dumps(doc), encoding="utf-8")

            def fake_branch() -> str:
                return "feature-PROJ-1-local"

            pol.current_git_branch = fake_branch  # type: ignore[method-assign]

            err = pol.ensure_lock_for_write("pipelines/ingest/foo/bar.py")
            self.assertIsNotNone(err)
            self.assertIn("locked", err.lower())


class SparkPostAdvisoryTests(unittest.TestCase):
    def test_post_tool_suggests_for_pipeline_antipattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = "pipelines/demo/bad.py"
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("df = df.repartition(1)\n", encoding="utf-8")
            saved = pol.REPO_ROOT
            try:
                pol.REPO_ROOT = root  # type: ignore[misc]
                payload = {"tool_name": "Write", "tool_input": {"path": rel, "contents": ""}}
                with unittest.mock.patch.object(pol, "read_stdin_json", return_value=payload):
                    with unittest.mock.patch.object(pol, "exit_post_additional_context") as m_ctx:
                        with unittest.mock.patch.object(pol, "exit_post_empty"):
                            pol.main_spark_post_tool()
                self.assertTrue(m_ctx.called)
                hint = m_ctx.call_args[0][0]
                self.assertIn("non-blocking", hint.lower())
                self.assertIn("repartition", hint.lower())
            finally:
                pol.REPO_ROOT = saved  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
