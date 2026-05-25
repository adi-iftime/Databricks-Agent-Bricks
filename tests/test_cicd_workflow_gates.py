"""CI workflow gate checks for SCRUM-122."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github/workflows/databricks-cicd.yml"


class TestCicdWorkflowGates(unittest.TestCase):
    def test_bundle_validate_command_present(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("databricks bundle validate -t dev", text)

    def test_auth_job_present(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("databricks-auth:", text)
        self.assertIn("DATABRICKS_HOST", text)
        self.assertIn("DATABRICKS_TOKEN", text)

    def test_cli_version_pinned_for_terraform_gpg_fix(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("version: 0.299.2", text)


if __name__ == "__main__":
    unittest.main()
