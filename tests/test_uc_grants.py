"""UC RBAC grant asset checks for SCRUM-133."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
GRANTS_SQL = REPO_ROOT / "resources/grants/00_dev_grants.sql"
RBAC_DOC = REPO_ROOT / "docs/security/uc-rbac.md"

INGESTION_SP = "mlops-ingestion-sp"
AGENT_SP = "mlops-agent-sp"
BRONZE_TABLES = (
    "pipeline_runs",
    "system_metrics",
    "model_metrics",
    "feature_store_metrics",
)


class TestUcGrants(unittest.TestCase):
    def test_grants_sql_exists(self) -> None:
        self.assertTrue(GRANTS_SQL.is_file())

    def test_ingestion_sp_modify_bronze_tables(self) -> None:
        text = GRANTS_SQL.read_text()
        self.assertIn(INGESTION_SP, text)
        for table in BRONZE_TABLES:
            self.assertIn(
                f"bronze_ops.{table} TO `{INGESTION_SP}`",
                text,
                table,
            )

    def test_agent_sp_select_gold_only(self) -> None:
        text = GRANTS_SQL.read_text()
        self.assertIn(f"gold_ops TO `{AGENT_SP}`", text)
        self.assertIn(f"SELECT ON SCHEMA mlops_intelligence_dev.gold_ops TO `{AGENT_SP}`", text)
        self.assertNotIn(f"bronze_ops TO `{AGENT_SP}`", text)
        self.assertNotIn(f"MODIFY ON TABLE", text.split(AGENT_SP)[-1])

    def test_rbac_doc_grant_matrix(self) -> None:
        self.assertTrue(RBAC_DOC.is_file())
        text = RBAC_DOC.read_text()
        self.assertIn(INGESTION_SP, text)
        self.assertIn(AGENT_SP, text)
        self.assertIn("Grant matrix", text)
        self.assertIn("Negative tests", text)


if __name__ == "__main__":
    unittest.main()
