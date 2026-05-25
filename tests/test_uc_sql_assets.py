"""Unity Catalog SQL asset checks for SCRUM-130."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_SQL = REPO_ROOT / "resources/sql/00_catalog.sql"


class TestUcSqlAssets(unittest.TestCase):
    def test_catalog_sql_exists(self) -> None:
        self.assertTrue(CATALOG_SQL.is_file())

    def test_catalog_sql_defines_schemas(self) -> None:
        text = CATALOG_SQL.read_text()
        self.assertIn("CREATE CATALOG", text)
        for schema in ("bronze_ops", "silver_ops", "gold_ops"):
            self.assertIn(schema, text)

    def test_unity_catalog_doc_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "docs/data/unity-catalog.md").is_file())


if __name__ == "__main__":
    unittest.main()
