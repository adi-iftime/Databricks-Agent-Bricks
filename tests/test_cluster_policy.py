"""Cluster policy variable checks for SCRUM-129."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
JOBS_DIR = REPO_ROOT / "resources" / "jobs"


class TestClusterPolicy(unittest.TestCase):
    def test_cluster_policy_variable_in_bundle(self) -> None:
        text = (REPO_ROOT / "databricks.yml").read_text()
        self.assertIn("cluster_policy_id:", text)

    def test_cluster_policy_doc_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "docs/operations/cluster-policies.md").is_file())


if __name__ == "__main__":
    unittest.main()
