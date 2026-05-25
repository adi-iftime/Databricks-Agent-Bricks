"""Notebook sync configuration checks for SCRUM-128."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestNotebookSync(unittest.TestCase):
    def test_sync_paths_include_notebooks(self) -> None:
        text = (REPO_ROOT / "databricks.yml").read_text()
        self.assertIn("notebooks", text)

    def test_domain_stub_notebooks_exist(self) -> None:
        for domain in ("ingestion", "ml_obs", "anomaly", "agent"):
            path = REPO_ROOT / "notebooks" / domain / "stub.py"
            self.assertTrue(path.is_file(), domain)


if __name__ == "__main__":
    unittest.main()
