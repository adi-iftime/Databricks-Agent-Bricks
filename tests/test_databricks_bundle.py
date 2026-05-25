"""Databricks bundle manifest checks for SCRUM-125/126."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "databricks.yml"


class TestDatabricksBundle(unittest.TestCase):
    def test_bundle_file_exists(self) -> None:
        self.assertTrue(BUNDLE_PATH.is_file())

    def test_required_bundle_keys(self) -> None:
        text = BUNDLE_PATH.read_text()
        self.assertIn("name: mlops_intelligence", text)
        self.assertIn("include:", text)
        self.assertIn("sync:", text)
        self.assertIn("variables:", text)
        self.assertIn("catalog:", text)
        self.assertIn("targets:", text)

    def test_multi_environment_targets(self) -> None:
        text = BUNDLE_PATH.read_text()
        for target in ("dev:", "staging:", "prod:"):
            self.assertIn(target, text)
        self.assertIn("mlops_intelligence_dev", text)
        self.assertIn("mlops_intelligence_staging", text)
        self.assertIn("mlops_intelligence_prod", text)

    def test_documentation_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "docs/architecture/dab.md").is_file())


if __name__ == "__main__":
    unittest.main()
