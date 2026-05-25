"""Databricks bundle manifest checks for SCRUM-125/126."""

from pathlib import Path
import re
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

    def test_dev_target_configured(self) -> None:
        text = BUNDLE_PATH.read_text()
        self.assertIn("dev:", text)
        self.assertIn("mlops_intelligence_dev", text)
        self.assertNotIn("staging:", text)
        self.assertNotIn("prod:", text)

    def test_documentation_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "docs/architecture/dab.md").is_file())

    def test_workspace_current_user_uses_string_field(self) -> None:
        """Bare ${workspace.current_user} is a map and breaks bundle validate."""
        text = BUNDLE_PATH.read_text()
        self.assertIsNone(
            re.search(r"\$\{workspace\.current_user\}(?!\.)", text),
            "Use ${workspace.current_user.userName} in string substitutions",
        )


if __name__ == "__main__":
    unittest.main()
