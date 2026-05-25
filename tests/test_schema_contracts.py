"""Schema contract checks for SCRUM-131."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestSchemaContracts(unittest.TestCase):
    def test_telemetry_sql_exists(self) -> None:
        path = REPO_ROOT / "resources/sql/01_telemetry_tables.sql"
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertIn("pipeline_runs", text)
        self.assertIn("system_metrics", text)

    def test_schema_contract_files(self) -> None:
        for name in ("pipeline_runs.yaml", "system_metrics.yaml"):
            path = REPO_ROOT / "resources/schema" / name
            self.assertTrue(path.is_file(), name)
            self.assertIn("columns:", path.read_text())

    def test_table_docs_exist(self) -> None:
        for name in ("pipeline_runs.md", "system_metrics.md"):
            self.assertTrue((REPO_ROOT / "docs/data/tables" / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
