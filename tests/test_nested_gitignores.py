import os
import tempfile
from pathlib import Path

import pytest

from llm_context.file_selector import GitIgnorer


class TestNestedGitignores:
    @pytest.fixture
    def temp_project(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            (project_root / "src").mkdir()
            (project_root / "src" / "utils").mkdir()
            (project_root / "tests").mkdir()
            (project_root / "docs").mkdir()
            (project_root / "README.md").touch()
            (project_root / "src" / "main.py").touch()
            (project_root / "src" / "utils" / "helper.py").touch()
            (project_root / "src" / "utils" / "temp.log").touch()
            (project_root / "tests" / "test_main.py").touch()
            (project_root / "tests" / "coverage.xml").touch()
            (project_root / "docs" / "guide.md").touch()
            (project_root / "build.log").touch()
            (project_root / ".gitignore").write_text("*.log\nbuild/\n__pycache__/\n")
            (project_root / "src" / "utils" / ".gitignore").write_text("*.tmp\n*.cache\n")
            (project_root / "tests" / ".gitignore").write_text("coverage.xml\n*.pyc\n")
            yield project_root

    def test_collects_all_gitignores(self, temp_project):
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        assert len(ignorer.ignorer_data) == 3

    def test_hierarchical_sorting(self, temp_project):
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        paths = [path for path, _ in ignorer.ignorer_data]
        assert "/src/utils" in paths
        assert "/tests" in paths
        assert "/" in paths
        src_utils_idx = paths.index("/src/utils")
        root_idx = paths.index("/")
        assert src_utils_idx < root_idx

    def test_root_gitignore_ignores_logs(self, temp_project):
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        assert ignorer.ignore("/build.log")
        assert ignorer.ignore("/src/utils/temp.log")

    def test_nested_gitignore_adds_patterns(self, temp_project):
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        (temp_project / "src" / "utils" / "cache.tmp").touch()
        assert ignorer.ignore("/src/utils/cache.tmp")
        (temp_project / "src" / "utils" / "data.cache").touch()
        assert ignorer.ignore("/src/utils/data.cache")
        assert ignorer.ignore("/tests/coverage.xml")

    def test_patterns_only_apply_to_subdirectories(self, temp_project):
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        (temp_project / "src" / "coverage.xml").touch()
        assert not ignorer.ignore("/src/coverage.xml")
        (temp_project / "tests" / "temp.tmp").touch()
        assert not ignorer.ignore("/tests/temp.tmp")

    def test_empty_gitignore_handling(self, temp_project):
        (temp_project / "docs" / ".gitignore").write_text("\n\n  \n")
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        assert not ignorer.ignore("/docs/guide.md")

    def test_gitignore_with_comments(self, temp_project):
        """Test .gitignore files with comments and blank lines"""
        gitignore_content = """
# This is a comment
*.backup

# Another comment
temp/
        """
        (temp_project / "docs" / ".gitignore").write_text(gitignore_content)
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        (temp_project / "docs" / "old.backup").touch()
        assert ignorer.ignore("/docs/old.backup")

    def test_relative_path_calculation(self, temp_project):
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        (temp_project / "src" / "utils" / "deep").mkdir()
        (temp_project / "src" / "utils" / "deep" / "nested.tmp").touch()
        assert ignorer.ignore("/src/utils/deep/nested.tmp")

    def test_extra_root_patterns_with_nested_gitignores(self, temp_project):
        extra_patterns = ["*.secret", "config.local"]
        ignorer = GitIgnorer.from_git_root(str(temp_project), extra_patterns)
        (temp_project / "api.secret").touch()
        assert ignorer.ignore("/api.secret")
        (temp_project / "src" / "db.secret").touch()
        assert ignorer.ignore("/src/db.secret")
        (temp_project / "src" / "utils" / "cache.tmp").touch()
        assert ignorer.ignore("/src/utils/cache.tmp")

    def test_directory_patterns(self, temp_project):
        ignorer = GitIgnorer.from_git_root(str(temp_project))
        (temp_project / "build").mkdir()
        (temp_project / "build" / "output.txt").touch()
        assert ignorer.ignore("/build/output.txt")
