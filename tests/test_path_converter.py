import unittest
from pathlib import Path

from llm_context.context_generator import PathConverter


class TestPathConverter(unittest.TestCase):
    def setUp(self):
        self.path_converter = PathConverter(Path("/home/user/project"))

    def test_init(self):
        self.assertEqual(self.path_converter.root, Path("/home/user/project"))
        self.assertEqual(self.path_converter.root.name, "project")

    def test_validate_valid_paths(self):
        valid_paths = ["/project/src/main.py", "/project/tests/test_main.py", "/project/README.md"]
        self.assertTrue(self.path_converter.validate(valid_paths))

    def test_validate_invalid_paths(self):
        invalid_paths = [
            "project/src/main.py",  # Missing leading slash
            "/projects/tests/test_main.py",  # Incorrect root name
            "/project",  # No path after root name
            "/otherproject/README.md",  # Wrong project name
        ]
        self.assertFalse(self.path_converter.validate(invalid_paths))

    def test_validate_mixed_paths(self):
        mixed_paths = [
            "/project/src/main.py",
            "/otherproject/README.md",
            "/project/tests/test_main.py",
        ]
        self.assertFalse(self.path_converter.validate(mixed_paths))

    def test_to_absolute_conversion(self):
        relative_paths = [
            "/project/src/main.py",
            "/project/tests/test_main.py",
            "/project/README.md",
        ]
        expected_absolute_paths = [
            "/home/user/project/src/main.py",
            "/home/user/project/tests/test_main.py",
            "/home/user/project/README.md",
        ]
        self.assertEqual(self.path_converter.to_absolute(relative_paths), expected_absolute_paths)

    def test_to_absolute_with_invalid_paths(self):
        invalid_paths = ["/otherproject/src/main.py", "project/tests/test_main.py", "/project"]
        with self.assertRaises(ValueError):
            self.path_converter.to_absolute(invalid_paths)

    def test_to_absolute_empty_list(self):
        self.assertEqual(self.path_converter.to_absolute([]), [])

    def test_validate_empty_list(self):
        self.assertTrue(self.path_converter.validate([]))


if __name__ == "__main__":
    unittest.main()
