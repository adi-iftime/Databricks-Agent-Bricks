"""Promotion workflow checks for SCRUM-124."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github/workflows/databricks-deploy-promotion.yml"


class TestPromotionWorkflow(unittest.TestCase):
    def test_workflow_dispatch_inputs(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("staging", text)
        self.assertIn("prod", text)
        self.assertIn("git_ref:", text)

    def test_validate_before_deploy(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("databricks bundle validate -t", text)
        self.assertIn("databricks bundle deploy -t", text)

    def test_prod_ref_guard(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn('TARGET" = "prod"', text)
        self.assertIn("main", text)

    def test_github_environments(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("environment: ${{ github.event.inputs.target }}", text)

    def test_cli_version_pinned(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("version: 0.299.2", text)

    def test_promotion_doc_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "docs/cicd/promotion.md").is_file())


if __name__ == "__main__":
    unittest.main()
