"""Schema contract checks for SCRUM-131/132."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]

TELEMETRY_TABLES = ("pipeline_runs", "system_metrics")
ML_METRICS_TABLES = ("model_metrics", "feature_store_metrics")
ALL_TABLES = TELEMETRY_TABLES + ML_METRICS_TABLES


class TestSchemaContracts(unittest.TestCase):
    def test_telemetry_sql_exists(self) -> None:
        path = REPO_ROOT / "resources/sql/01_telemetry_tables.sql"
        self.assertTrue(path.is_file())
        text = path.read_text()
        for table in TELEMETRY_TABLES:
            self.assertIn(table, text)

    def test_ml_metrics_sql_exists(self) -> None:
        path = REPO_ROOT / "resources/sql/02_ml_metrics_tables.sql"
        self.assertTrue(path.is_file())
        text = path.read_text()
        for table in ML_METRICS_TABLES:
            self.assertIn(table, text)

    def test_schema_contract_files(self) -> None:
        for name in ALL_TABLES:
            path = REPO_ROOT / "resources/schema" / f"{name}.yaml"
            self.assertTrue(path.is_file(), name)
            self.assertIn("columns:", path.read_text())

    def test_table_docs_exist(self) -> None:
        for name in ALL_TABLES:
            self.assertTrue((REPO_ROOT / "docs/data/tables" / f"{name}.md").is_file(), name)


if __name__ == "__main__":
    unittest.main()
