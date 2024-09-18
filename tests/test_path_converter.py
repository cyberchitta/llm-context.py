import unittest
from pathlib import Path

from llm_context.utils import PathConverter


class TestPathConverter(unittest.TestCase):
    def setUp(self):
        self.converter = PathConverter.create(Path("/home/user/project"))

    def test_init(self):
        self.assertEqual(self.converter.root, Path("/home/user/project"))
        self.assertEqual(self.converter.root.name, "project")

    def test_validate_valid_paths(self):
        valid_paths = ["/project/src/main.py", "/project/tests/test_main.py", "/project/README.md"]
        self.assertTrue(self.converter.validate(valid_paths))

    def test_validate_invalid_paths(self):
        invalid_paths = [
            "project/src/main.py",  # Missing leading slash
            "/projects/tests/test_main.py",  # Incorrect root name
            "/project",  # No path after root name
            "/otherproject/README.md",  # Wrong project name
        ]
        self.assertFalse(self.converter.validate(invalid_paths))

    def test_validate_mixed_paths(self):
        mixed_paths = [
            "/project/src/main.py",
            "/otherproject/README.md",
            "/project/tests/test_main.py",
        ]
        self.assertFalse(self.converter.validate(mixed_paths))

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
        self.assertEqual(self.converter.to_absolute(relative_paths), expected_absolute_paths)

    def test_to_relative_conversion(self):
        absolute_paths = [
            "/home/user/project/src/main.py",
            "/home/user/project/tests/test_main.py",
            "/home/user/project/README.md",
        ]
        expected_relative_paths = [
            "/project/src/main.py",
            "/project/tests/test_main.py",
            "/project/README.md",
        ]
        self.assertEqual(self.converter.to_relative(absolute_paths), expected_relative_paths)

    def test_to_absolute_empty_list(self):
        self.assertEqual(self.converter.to_absolute([]), [])

    def test_validate_empty_list(self):
        self.assertTrue(self.converter.validate([]))


if __name__ == "__main__":
    unittest.main()
