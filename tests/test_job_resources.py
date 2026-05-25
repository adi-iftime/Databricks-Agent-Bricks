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

    def test_jobs_avoid_bundle_validate_map_interpolation_traps(self) -> None:
        """Job-level tags, dotted spark_conf, and SingleNode custom_tags break bundle validate."""
        for job_file in JOBS_DIR.glob("*.job.yml"):
            text = job_file.read_text()
            self.assertNotIn("spark_conf:", text, job_file.name)
            self.assertNotIn("\n      tags:", text, job_file.name)
            self.assertNotIn("custom_tags:", text, job_file.name)
            self.assertIn("num_workers: 1", text, job_file.name)

    def test_bundle_includes_jobs_path(self) -> None:
        text = (REPO_ROOT / "databricks.yml").read_text()
        self.assertIn("resources/jobs/*.yml", text)

    def test_job_notebook_paths_include_extension(self) -> None:
        for job_file in JOBS_DIR.glob("*.job.yml"):
            text = job_file.read_text()
            self.assertIn("notebook_path:", text, job_file.name)
            self.assertRegex(
                text,
                r"notebook_path: \.\./\.\./notebooks/[-\w]+/stub\.py",
                job_file.name,
            )


if __name__ == "__main__":
    unittest.main()
