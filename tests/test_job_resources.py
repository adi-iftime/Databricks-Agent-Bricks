"""DAB job resource checks for SCRUM-127."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
JOBS_DIR = REPO_ROOT / "resources" / "jobs"

EXPECTED_JOBS = (
    "ingestion.job.yml",
    "ml_observability.job.yml",
    "anomaly_detection.job.yml",
    "agent_analysis.job.yml",
)


class TestJobResources(unittest.TestCase):
    def test_job_files_exist(self) -> None:
        missing = [name for name in EXPECTED_JOBS if not (JOBS_DIR / name).is_file()]
        self.assertEqual(missing, [], f"Missing job resources: {missing}")

    def test_jobs_documentation_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "docs/architecture/jobs.md").is_file())

    def test_bundle_includes_jobs_path(self) -> None:
        text = (REPO_ROOT / "databricks.yml").read_text()
        self.assertIn("resources/jobs/*.yml", text)


if __name__ == "__main__":
    unittest.main()
