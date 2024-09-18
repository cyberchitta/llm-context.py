import unittest

from llm_context.file_selector import PathspecIgnorer


class TestPathspecIgnorerBasicFunctionality(unittest.TestCase):
    def test_basename_ignore(self):
        ignorer = PathspecIgnorer.create(["*.txt", "temp/"])
        self.assertTrue(ignorer.ignore("/path/to/file.txt"))
        self.assertFalse(ignorer.ignore("/path/to/file.py"))
        self.assertTrue(ignorer.ignore("/path/to/temp/"))

    def test_path_ignore(self):
        ignorer = PathspecIgnorer.create(["/root/*.log", "**/temp/"])
        self.assertTrue(ignorer.ignore("/root/file.log"))
        self.assertFalse(ignorer.ignore("/other/file.log"))
        self.assertTrue(ignorer.ignore("/path/to/temp/file"))


class TestGitignoreSemantics(unittest.TestCase):
    def test_text_files_with_exception(self):
        patterns = ["*.txt", "!dir1/*.txt"]
        ignorer = PathspecIgnorer.create(patterns)

        self.assertTrue(ignorer.ignore("/project/file1.txt"))
        self.assertFalse(ignorer.ignore("/project/file2.py"))
        #        self.assertFalse(ignorer.ignore("/project/dir1/file3.txt"))
        self.assertTrue(ignorer.ignore("/project/dir2/file4.txt"))
        self.assertFalse(ignorer.ignore("/project/dir1"))
        self.assertFalse(ignorer.ignore("/project/dir2"))

    def test_directory_and_python_files(self):
        patterns = ["dir1/", "*.py"]
        ignorer = PathspecIgnorer.create(patterns)

        self.assertFalse(ignorer.ignore("/project/file1.txt"))
        self.assertTrue(ignorer.ignore("/project/file2.py"))
        self.assertTrue(ignorer.ignore("/project/dir1/file3.txt"))
        self.assertTrue(ignorer.ignore("/project/dir1/"))
        self.assertTrue(ignorer.ignore("/project/dir2/file4.py"))
        self.assertFalse(ignorer.ignore("/project/dir2"))

    def test_node_modules_dist_and_logs(self):
        patterns = ["**/node_modules/", "dist/", "*.log"]
        ignorer = PathspecIgnorer.create(patterns)

        self.assertFalse(ignorer.ignore("/project/file1.txt"))
        self.assertTrue(ignorer.ignore("/project/dir1/node_modules/file.js"))
        self.assertTrue(ignorer.ignore("/project/dir1/node_modules/"))
        self.assertTrue(ignorer.ignore("/project/dir2/dist/file.js"))
        self.assertTrue(ignorer.ignore("/project/dir2/dist/"))
        self.assertTrue(ignorer.ignore("/project/dir3/file.log"))
        self.assertTrue(ignorer.ignore("/project/dir4/subdir/deep/file.log"))


class TestPathspecIgnorer(unittest.TestCase):
    def test_simple_filename(self):
        ignorer = PathspecIgnorer.create(["*.txt"])
        self.assertTrue(ignorer.ignore("file.txt"))
        self.assertFalse(ignorer.ignore("file.py"))

    def test_directory_pattern(self):
        ignorer = PathspecIgnorer.create(["dir/"])
        self.assertTrue(ignorer.ignore("dir/"))

    def test_negation(self):
        ignorer = PathspecIgnorer.create(["*.txt", "!important.txt"])
        self.assertTrue(ignorer.ignore("file.txt"))
        self.assertFalse(ignorer.ignore("important.txt"))

    def test_root_directory_pattern(self):
        ignorer = PathspecIgnorer.create(["/root"])
        self.assertTrue(ignorer.ignore("root"))
        self.assertFalse(ignorer.ignore("subdir/root"))

    def test_nested_directory_pattern(self):
        ignorer = PathspecIgnorer.create(["**/logs"])
        self.assertTrue(ignorer.ignore("logs"))
        self.assertTrue(ignorer.ignore("dir/logs"))
        self.assertTrue(ignorer.ignore("dir/subdir/logs"))
        self.assertFalse(ignorer.ignore("dir/logs-file.txt"))

    def test_complex_pattern(self):
        ignorer = PathspecIgnorer.create(["*.py[cod]"])
        self.assertTrue(ignorer.ignore("file.pyc"))
        self.assertTrue(ignorer.ignore("file.pyo"))
        self.assertTrue(ignorer.ignore("file.pyd"))
        self.assertFalse(ignorer.ignore("file.py"))

    def test_multiple_directory_pattern(self):
        ignorer = PathspecIgnorer.create(["/priv/static"])
        self.assertFalse(ignorer.ignore("priv"))
        self.assertTrue(ignorer.ignore("priv/static"))
        self.assertFalse(ignorer.ignore("other/priv/static"))

    def test_multiple_directory_pattern_with_wildcard(self):
        ignorer = PathspecIgnorer.create(["docs/**/secret"])
        self.assertFalse(ignorer.ignore("docs"))
        self.assertTrue(ignorer.ignore("docs/secret"))
        self.assertTrue(ignorer.ignore("docs/project/secret"))
        self.assertTrue(ignorer.ignore("docs/project/subproject/secret"))
        self.assertFalse(ignorer.ignore("secret"))
        self.assertFalse(ignorer.ignore("other/docs/secret"))

    def test_single_asterisk(self):
        ignorer = PathspecIgnorer.create(["*.log"])
        self.assertTrue(ignorer.ignore("file.log"))
        self.assertTrue(ignorer.ignore("folder/file.log"))
        self.assertFalse(ignorer.ignore("file.txt"))

    def test_double_asterisk(self):
        ignorer = PathspecIgnorer.create(["**/node_modules"])
        self.assertTrue(ignorer.ignore("node_modules"))
        self.assertTrue(ignorer.ignore("folder/node_modules"))
        self.assertTrue(ignorer.ignore("folder/subfolder/node_modules"))

    def test_question_mark(self):
        ignorer = PathspecIgnorer.create(["file?.txt"])
        self.assertTrue(ignorer.ignore("file1.txt"))
        self.assertTrue(ignorer.ignore("fileA.txt"))
        self.assertFalse(ignorer.ignore("file10.txt"))

    def test_character_class(self):
        ignorer = PathspecIgnorer.create(["file[0-9].txt"])
        self.assertTrue(ignorer.ignore("file0.txt"))
        self.assertTrue(ignorer.ignore("file5.txt"))
        self.assertFalse(ignorer.ignore("fileA.txt"))

    def test_negation_with_wildcard(self):
        ignorer = PathspecIgnorer.create(["*.log", "!important.log"])
        self.assertTrue(ignorer.ignore("debug.log"))
        self.assertFalse(ignorer.ignore("important.log"))
        self.assertFalse(ignorer.ignore("logs/important.log"))

    def test_trailing_spaces(self):
        ignorer = PathspecIgnorer.create(["*.log ", "!important.log "])
        self.assertTrue(ignorer.ignore("file.log"))
        self.assertFalse(ignorer.ignore("important.log"))

    def test_directory_vs_file(self):
        ignorer = PathspecIgnorer.create(["logs"])
        self.assertTrue(ignorer.ignore("logs"))
        self.assertTrue(ignorer.ignore("logs"))
        self.assertFalse(ignorer.ignore("logs.txt"))


if __name__ == "__main__":
    unittest.main()
