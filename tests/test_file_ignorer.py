import unittest
from src.file_ignorer import FileIgnorer


class TestFileIgnorer(unittest.TestCase):
    def test_simple_filename(self):
        ignorer = FileIgnorer.create(["*.txt"])
        self.assertTrue(ignorer.ignore("file.txt", False))
        self.assertFalse(ignorer.ignore("file.py", False))

    def test_directory_pattern(self):
        ignorer = FileIgnorer.create(["dir/"])
        self.assertTrue(ignorer.ignore("dir", True))

    def test_negation(self):
        ignorer = FileIgnorer.create(["*.txt", "!important.txt"])
        self.assertTrue(ignorer.ignore("file.txt", False))
        self.assertFalse(ignorer.ignore("important.txt", False))

    def test_root_directory_pattern(self):
        ignorer = FileIgnorer.create(["/root"])
        self.assertTrue(ignorer.ignore("root", True))
        self.assertFalse(ignorer.ignore("subdir/root", True))

    def test_nested_directory_pattern(self):
        ignorer = FileIgnorer.create(["**/logs"])
        self.assertTrue(ignorer.ignore("logs", True))
        self.assertTrue(ignorer.ignore("dir/logs", True))
        self.assertTrue(ignorer.ignore("dir/subdir/logs", True))
        self.assertFalse(ignorer.ignore("dir/logs-file.txt", False))

    def test_complex_pattern(self):
        ignorer = FileIgnorer.create(["*.py[cod]"])
        self.assertTrue(ignorer.ignore("file.pyc", False))
        self.assertTrue(ignorer.ignore("file.pyo", False))
        self.assertTrue(ignorer.ignore("file.pyd", False))
        self.assertFalse(ignorer.ignore("file.py", False))

    def test_comment_and_empty_lines(self):
        ignorer = FileIgnorer.create(["# This is a comment", "", "*.txt"])
        self.assertTrue(ignorer.ignore("file.txt", False))
        self.assertFalse(ignorer.ignore("# This is a comment", False))

    def test_multiple_directory_pattern(self):
        ignorer = FileIgnorer.create(["/priv/static"])
        self.assertFalse(ignorer.ignore("priv", True))
        self.assertTrue(ignorer.ignore("priv/static", True))
        self.assertFalse(ignorer.ignore("other/priv/static", True))

    def test_multiple_directory_pattern_with_wildcard(self):
        ignorer = FileIgnorer.create(["docs/**/secret"])
        self.assertFalse(ignorer.ignore("docs", True))
        self.assertTrue(ignorer.ignore("docs/secret", True))
        self.assertTrue(ignorer.ignore("docs/project/secret", True))
        self.assertTrue(ignorer.ignore("docs/project/subproject/secret", True))
        self.assertFalse(ignorer.ignore("secret", True))
        self.assertFalse(ignorer.ignore("other/docs/secret", True))

    def test_single_asterisk(self):
        ignorer = FileIgnorer.create(["*.log"])
        self.assertTrue(ignorer.ignore("file.log", False))
        self.assertTrue(ignorer.ignore("folder/file.log", False))
        self.assertFalse(ignorer.ignore("file.txt", False))

    def test_double_asterisk(self):
        ignorer = FileIgnorer.create(["**/node_modules"])
        self.assertTrue(ignorer.ignore("node_modules", True))
        self.assertTrue(ignorer.ignore("folder/node_modules", True))
        self.assertTrue(ignorer.ignore("folder/subfolder/node_modules", True))

    def test_question_mark(self):
        ignorer = FileIgnorer.create(["file?.txt"])
        self.assertTrue(ignorer.ignore("file1.txt", False))
        self.assertTrue(ignorer.ignore("fileA.txt", False))
        self.assertFalse(ignorer.ignore("file10.txt", False))

    def test_character_class(self):
        ignorer = FileIgnorer.create(["file[0-9].txt"])
        self.assertTrue(ignorer.ignore("file0.txt", False))
        self.assertTrue(ignorer.ignore("file5.txt", False))
        self.assertFalse(ignorer.ignore("fileA.txt", False))

    def test_negation_with_wildcard(self):
        ignorer = FileIgnorer.create(["*.log", "!important.log"])
        self.assertTrue(ignorer.ignore("debug.log", False))
        self.assertFalse(ignorer.ignore("important.log", False))
        self.assertTrue(ignorer.ignore("logs/important.log", False))

    def test_trailing_spaces(self):
        ignorer = FileIgnorer.create(["*.log ", "!important.log "])
        self.assertTrue(ignorer.ignore("file.log", False))
        self.assertFalse(ignorer.ignore("important.log", False))

    def test_directory_vs_file(self):
        ignorer = FileIgnorer.create(["logs"])
        self.assertTrue(ignorer.ignore("logs", True))
        self.assertTrue(ignorer.ignore("logs", False))
        self.assertFalse(ignorer.ignore("logs.txt", False))


if __name__ == "__main__":
    unittest.main()
