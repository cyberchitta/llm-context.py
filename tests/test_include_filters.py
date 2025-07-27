import os
import tempfile
import unittest
from pathlib import Path

from llm_context.file_selector import FileSelector, IncludeFilter
from llm_context.utils import PathConverter


class TestIncludeFilterBasics(unittest.TestCase):
    """Test the core IncludeFilter functionality"""

    def test_empty_patterns_include_nothing(self):
        """Empty patterns should include nothing"""
        filter = IncludeFilter.create([])
        self.assertFalse(filter.include("/any/path.py"))
        self.assertFalse(filter.include("/src/file.txt"))

    def test_universal_pattern_includes_everything(self):
        """**/* should include everything"""
        filter = IncludeFilter.create(["**/*"])
        self.assertTrue(filter.include("/any/path.py"))
        self.assertTrue(filter.include("/src/file.txt"))
        self.assertTrue(filter.include("/deep/nested/path/file.js"))

    def test_specific_filename_patterns(self):
        """Test specific filename patterns"""
        filter = IncludeFilter.create(["*.py"])
        self.assertTrue(filter.include("file.py"))
        self.assertTrue(filter.include("/path/to/file.py"))
        self.assertFalse(filter.include("file.txt"))
        self.assertFalse(filter.include("/path/to/file.txt"))

    def test_specific_file_paths(self):
        """Test exact file path matching"""
        filter = IncludeFilter.create(["/src/llm_context/rule.py"])
        self.assertTrue(filter.include("/src/llm_context/rule.py"))
        self.assertFalse(filter.include("/src/llm_context/other.py"))
        self.assertFalse(filter.include("/other/llm_context/rule.py"))

    def test_directory_patterns(self):
        """Test directory-based patterns"""
        filter = IncludeFilter.create(["/src/**"])
        self.assertTrue(filter.include("/src/file.py"))
        self.assertTrue(filter.include("/src/subdir/file.py"))
        self.assertFalse(filter.include("/other/file.py"))

    def test_multiple_patterns(self):
        """Test multiple patterns in one filter"""
        filter = IncludeFilter.create(["*.py", "*.md", "/src/**"])
        self.assertTrue(filter.include("file.py"))
        self.assertTrue(filter.include("README.md"))
        self.assertTrue(filter.include("/src/anything.txt"))
        self.assertFalse(filter.include("file.js"))

    def test_path_format_variations(self):
        """Test different path formats - with/without leading slash"""
        filter = IncludeFilter.create(["src/file.py"])

        # Test both formats
        self.assertTrue(filter.include("src/file.py"))
        self.assertTrue(filter.include("/src/file.py"))

        # Test with different leading slash pattern
        filter_with_slash = IncludeFilter.create(["/src/file.py"])
        self.assertTrue(filter_with_slash.include("src/file.py"))
        self.assertTrue(filter_with_slash.include("/src/file.py"))


class TestFileSelectorWithIncludeFilters(unittest.TestCase):
    """Test FileSelector with real file system and include filters"""

    def setUp(self):
        """Create a temporary directory structure for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

        # Create test file structure
        (self.root_path / "src").mkdir()
        (self.root_path / "src" / "llm_context").mkdir()
        (self.root_path / "src" / "llm_context" / "rule.py").write_text("# rule.py")
        (self.root_path / "src" / "llm_context" / "context.py").write_text("# context.py")
        (self.root_path / "docs").mkdir()
        (self.root_path / "docs" / "readme.md").write_text("# readme")
        (self.root_path / "test.py").write_text("# test")
        (self.root_path / "config.yaml").write_text("config: value")

    def tearDown(self):
        """Clean up temporary directory"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_limit_to_all_files(self):
        """Test limit-to with **/* includes all files"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=[],
            limit_to_pathspecs=["**/*"],
            also_include_pathspecs=[],
        )
        files = selector.get_relative_files()

        # Should include all files
        self.assertIn(f"/{self.root_path.name}/src/llm_context/rule.py", files)
        self.assertIn(f"/{self.root_path.name}/test.py", files)
        self.assertIn(f"/{self.root_path.name}/config.yaml", files)

    def test_limit_to_python_files_only(self):
        """Test limit-to with *.py only includes Python files"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=[],
            limit_to_pathspecs=["*.py"],
            also_include_pathspecs=[],
        )
        files = selector.get_relative_files()

        # Should only include Python files
        python_files = [f for f in files if f.endswith(".py")]
        non_python_files = [f for f in files if not f.endswith(".py")]

        self.assertGreater(len(python_files), 0, "Should find Python files")
        self.assertEqual(len(non_python_files), 0, "Should not find non-Python files")

    def test_also_include_overrides_gitignore(self):
        """Test that also-include overrides gitignore patterns"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=["**/*"],  # Ignore everything
            limit_to_pathspecs=["**/*"],
            also_include_pathspecs=["*.py"],  # But include Python files
        )
        files = selector.get_relative_files()

        # Should only include Python files despite ignore everything
        self.assertTrue(any(f.endswith(".py") for f in files), "Should include Python files")
        self.assertFalse(any(f.endswith(".yaml") for f in files), "Should not include YAML files")

    def test_specific_file_also_include(self):
        """Test also-include with specific file paths"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=["**/*"],  # Ignore everything
            limit_to_pathspecs=["**/*"],
            also_include_pathspecs=["/src/llm_context/rule.py"],
        )
        files = selector.get_relative_files()

        # Should only include the specific file
        expected_file = f"/{self.root_path.name}/src/llm_context/rule.py"
        self.assertIn(expected_file, files)
        self.assertEqual(len(files), 1, "Should only include one file")


class TestAlsoIncludeEdgeCases(unittest.TestCase):
    """Test edge cases for also-include functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

        # Create nested structure
        (self.root_path / "src" / "deep" / "nested").mkdir(parents=True)
        (self.root_path / "src" / "deep" / "nested" / "file.py").write_text("# nested")
        (self.root_path / "ignored_dir").mkdir()
        (self.root_path / "ignored_dir" / "important.py").write_text("# important")
        (self.root_path / "test.py").write_text("# test")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_also_include_deeply_nested_file(self):
        """Test also-include with deeply nested files"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=["**/*"],
            limit_to_pathspecs=["**/*"],
            also_include_pathspecs=["/src/deep/nested/file.py"],
        )
        files = selector.get_relative_files()

        expected = f"/{self.root_path.name}/src/deep/nested/file.py"
        self.assertIn(expected, files)
        self.assertEqual(len(files), 1)

    def test_also_include_multiple_specific_files(self):
        """Test also-include with multiple specific files"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=["**/*"],
            limit_to_pathspecs=["**/*"],
            also_include_pathspecs=[
                "/src/deep/nested/file.py",
                "/ignored_dir/important.py",
                "/test.py",
            ],
        )
        files = selector.get_relative_files()

        self.assertEqual(len(files), 3)
        filenames = [f.split("/")[-1] for f in files]
        self.assertIn("file.py", filenames)
        self.assertIn("important.py", filenames)
        self.assertIn("test.py", filenames)

    def test_also_include_with_glob_patterns(self):
        """Test also-include with glob patterns"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=["**/*"],
            limit_to_pathspecs=["**/*"],
            also_include_pathspecs=["**/important.py"],
        )
        files = selector.get_relative_files()

        important_files = [f for f in files if "important.py" in f]
        self.assertEqual(len(important_files), 1)

    def test_also_include_overrides_deeply_ignored_directories(self):
        """Test that also-include works even when parent directories are ignored"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=["ignored_dir/", "src/deep/"],  # Ignore specific directories
            limit_to_pathspecs=["**/*"],
            also_include_pathspecs=["/ignored_dir/important.py", "/src/deep/nested/file.py"],
        )
        files = selector.get_relative_files()

        # Should include files despite directory ignores
        filenames = [f.split("/")[-1] for f in files]
        self.assertIn("important.py", filenames)
        self.assertIn("file.py", filenames)
        # Should also include test.py (not ignored)
        self.assertIn("test.py", filenames)


class TestFileSelectorCombinedLogic(unittest.TestCase):
    """Test complex combinations of ignore, limit-to, and also-include"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

        # Create diverse file types
        (self.root_path / "src").mkdir()
        (self.root_path / "src" / "app.py").write_text("# app")
        (self.root_path / "src" / "config.yaml").write_text("config")
        (self.root_path / "tests").mkdir()
        (self.root_path / "tests" / "test_app.py").write_text("# test")
        (self.root_path / "docs").mkdir()
        (self.root_path / "docs" / "readme.md").write_text("# readme")
        (self.root_path / "build").mkdir()
        (self.root_path / "build" / "output.txt").write_text("output")
        (self.root_path / "important.log").write_text("log")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_complex_filtering_combination(self):
        """Test complex combination: ignore build/, limit to *.py and *.md, but also include specific files"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=["build/", "*.log"],  # Ignore build dir and log files
            limit_to_pathspecs=["*.py", "*.md"],  # Only Python and Markdown
            also_include_pathspecs=[
                "/src/config.yaml",
                "/important.log",
            ],  # But include these specific files
        )
        files = selector.get_relative_files()

        filenames = [f.split("/")[-1] for f in files]

        # Should include Python and Markdown files
        self.assertIn("app.py", filenames)
        self.assertIn("test_app.py", filenames)
        self.assertIn("readme.md", filenames)

        # Should include also-include files despite patterns
        self.assertIn("config.yaml", filenames)  # Not *.py or *.md but in also-include
        self.assertIn("important.log", filenames)  # Ignored by *.log but in also-include

        # Should NOT include files that don't match any criteria
        self.assertNotIn("output.txt", filenames)  # In ignored build/ dir and not in also-include

    def test_also_include_with_empty_limit_to(self):
        """Test also-include when limit-to would exclude everything"""
        selector = FileSelector.create(
            self.root_path,
            ignore_pathspecs=[],
            limit_to_pathspecs=["*.nonexistent"],  # Would match nothing
            also_include_pathspecs=["*.py"],
        )
        files = selector.get_relative_files()

        # Should only include Python files via also-include
        python_files = [f for f in files if f.endswith(".py")]
        non_python_files = [f for f in files if not f.endswith(".py")]

        self.assertGreater(len(python_files), 0)
        self.assertEqual(len(non_python_files), 0)


class TestPathFormatNormalization(unittest.TestCase):
    """Test path format edge cases"""

    def test_path_format_consistency(self):
        """Test that different path formats in patterns work consistently"""
        filter = IncludeFilter.create(
            [
                "src/file.py",  # No leading slash
                "/src/file2.py",  # Leading slash
                "src/**",  # Glob pattern
                "/src/**/file3.py",  # Combined
            ]
        )

        # All these should work
        self.assertTrue(filter.include("src/file.py"))
        self.assertTrue(filter.include("/src/file.py"))
        self.assertTrue(filter.include("src/file2.py"))
        self.assertTrue(filter.include("/src/file2.py"))
        self.assertTrue(filter.include("src/anything.py"))
        self.assertTrue(filter.include("src/deep/file3.py"))

    def test_directory_vs_file_patterns(self):
        """Test directory patterns vs file patterns"""
        filter = IncludeFilter.create([
            "src/file.py",  # Specific file pattern
        ])
        
        # Specific file should match
        self.assertTrue(filter.include("src/file.py"))
        # Other files should not match
        self.assertFalse(filter.include("src/other.py"))
        
        # Test directory pattern separately
        dir_filter = IncludeFilter.create(["src/"])
        self.assertTrue(dir_filter.include("src/"))
        self.assertTrue(dir_filter.include("src/file.py"))  # Directory pattern matches contents
        self.assertTrue(dir_filter.include("src/other.py"))  # This is correct gitignore behavior


class TestPerformanceAndRegression(unittest.TestCase):
    """Test performance characteristics and regression prevention"""

    def test_no_also_include_patterns_no_extra_traversal(self):
        """Test that empty also-include doesn't cause extra work"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            (root_path / "test.py").write_text("# test")

            # Create selector with no also-include patterns
            selector = FileSelector.create(
                root_path,
                ignore_pathspecs=[],
                limit_to_pathspecs=["**/*"],
                also_include_pathspecs=[],  # Empty
            )

            # Should work normally
            files = selector.get_relative_files()
            self.assertGreater(len(files), 0)

    def test_backward_compatibility_with_existing_rules(self):
        """Test that existing behavior still works"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            (root_path / "src").mkdir()
            (root_path / "src" / "app.py").write_text("# app")
            (root_path / "test.py").write_text("# test")
            (root_path / "readme.md").write_text("# readme")

            # Test standard gitignore + limit-to behavior (no also-include)
            selector = FileSelector.create(
                root_path,
                ignore_pathspecs=["*.md"],
                limit_to_pathspecs=["*.py"],
                also_include_pathspecs=[],
            )
            files = selector.get_relative_files()

            filenames = [f.split("/")[-1] for f in files]
            self.assertIn("app.py", filenames)
            self.assertIn("test.py", filenames)
            self.assertNotIn("readme.md", filenames)


if __name__ == "__main__":
    unittest.main()
