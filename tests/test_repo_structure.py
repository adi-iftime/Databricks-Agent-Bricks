"""Repository layout checks for SCRUM-115 (DAB-aligned scaffold)."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "src/mlops_intelligence/__init__.py",
    "notebooks/README.md",
    "resources/README.md",
    "resources/jobs",
    "resources/sql",
    "docs/architecture/repo-layout.md",
    "databricks.yml",
]


class TestRepoStructure(unittest.TestCase):
    def test_required_paths_exist(self) -> None:
        missing = [p for p in REQUIRED_PATHS if not (REPO_ROOT / p).exists()]
        self.assertEqual(missing, [], f"Missing required paths: {missing}")

    def test_cursor_framework_preserved(self) -> None:
        self.assertTrue((REPO_ROOT / ".cursor").is_dir())
        self.assertTrue((REPO_ROOT / "tests" / "test_hook_policies.py").is_file())


if __name__ == "__main__":
    unittest.main()
