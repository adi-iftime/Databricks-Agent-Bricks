"""Audit and lineage tag asset checks for SCRUM-134."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
TAGS_SQL = REPO_ROOT / "resources/sql/03_audit_lineage_tags.sql"
AUDIT_DOC = REPO_ROOT / "docs/security/audit-lineage.md"

TABLES = (
    "pipeline_runs",
    "system_metrics",
    "model_metrics",
    "feature_store_metrics",
)
REQUIRED_TAG_KEYS = ("project", "domain", "layer")


class TestAuditLineageTags(unittest.TestCase):
    def test_tags_sql_exists(self) -> None:
        self.assertTrue(TAGS_SQL.is_file())

    def test_all_bronze_tables_tagged(self) -> None:
        text = TAGS_SQL.read_text()
        for table in TABLES:
            self.assertIn(f"bronze_ops.{table} SET TAGS", text, table)

    def test_project_tag_on_tables(self) -> None:
        text = TAGS_SQL.read_text()
        self.assertGreaterEqual(text.count("'project' = 'mlops_intelligence'"), len(TABLES))

    def test_schema_tags_defined(self) -> None:
        text = TAGS_SQL.read_text()
        for schema in ("bronze_ops", "silver_ops", "gold_ops"):
            self.assertIn(f"ALTER SCHEMA mlops_intelligence_dev.{schema} SET TAGS", text)

    def test_audit_doc_and_runbook(self) -> None:
        self.assertTrue(AUDIT_DOC.is_file())
        text = AUDIT_DOC.read_text()
        self.assertIn("system.access.audit", text)
        self.assertIn("mlops-agent-sp", text)
        self.assertIn("03_audit_lineage_tags.sql", text)


if __name__ == "__main__":
    unittest.main()
