"""Dependency-gap detection: what a selection references but does not include."""

import tempfile
import unittest
from pathlib import Path

from llm_context.dependencies import MAX_DEFINING_FILES, SymbolIndex
from llm_context.excerpters.parser import ASTFactory
from llm_context.excerpters.tagger import ASTBasedTagger


class DependencyGapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.name = self.root.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name: str, content: str) -> str:
        (self.root / name).write_text(content)
        return f"/{self.name}/{name}"

    def index(self, rel_paths):
        tagger = ASTBasedTagger.create(str(self.root), ASTFactory.create())
        return SymbolIndex.create(tagger, self.root, rel_paths)

    def test_names_the_file_defining_a_referenced_symbol(self):
        caller = self.write("caller.py", "def run():\n    return helper()\n")
        helper = self.write("helper.py", "def helper():\n    return 1\n")
        gaps = self.index([caller, helper]).gaps([caller])
        self.assertEqual([g.rel_path for g in gaps], [helper])
        self.assertEqual(gaps[0].symbols, ["helper"])
        self.assertEqual(gaps[0].reference_count, 1)

    def test_selected_files_are_never_reported_as_gaps(self):
        caller = self.write("caller.py", "def run():\n    return helper()\n")
        helper = self.write("helper.py", "def helper():\n    return 1\n")
        self.assertEqual(self.index([caller, helper]).gaps([caller, helper]), [])

    def test_ranks_by_reference_count(self):
        caller = self.write("caller.py", "def run():\n    return one() + two() + three()\n")
        few = self.write("few.py", "def one():\n    return 1\n")
        many = self.write("many.py", "def two():\n    return 2\n\ndef three():\n    return 3\n")
        gaps = self.index([caller, few, many]).gaps([caller])
        self.assertEqual([g.rel_path for g in gaps], [many, few])
        self.assertEqual(gaps[0].reference_count, 2)

    def ambiguous_fixture(self, owner_count: int):
        caller = self.write("caller.py", "def run():\n    return create()\n")
        owners = [
            self.write(f"owner{i}.py", "def create():\n    return 1\n") for i in range(owner_count)
        ]
        return caller, owners

    def test_ambiguous_symbols_are_dropped_rather_than_guessed(self):
        """A name defined in more files than the threshold is not attributed to any."""
        caller, owners = self.ambiguous_fixture(4)
        self.assertEqual(self.index([caller, *owners]).gaps([caller], max_defining_files=3), [])

    def test_symbol_defined_within_the_threshold_is_still_reported(self):
        caller, owners = self.ambiguous_fixture(3)
        gaps = self.index([caller, *owners]).gaps([caller], max_defining_files=3)
        self.assertEqual({g.rel_path for g in gaps}, set(owners))

    def test_default_threshold_is_small_enough_to_suppress_common_names(self):
        """Guards the default: raising it silently would flood the report."""
        self.assertLessEqual(MAX_DEFINING_FILES, 3)
        caller, owners = self.ambiguous_fixture(MAX_DEFINING_FILES + 1)
        self.assertEqual(self.index([caller, *owners]).gaps([caller]), [])

    def test_references_with_no_definition_anywhere_are_ignored(self):
        caller = self.write("caller.py", "import os\n\ndef run():\n    return os.getpid()\n")
        self.assertEqual(self.index([caller]).gaps([caller]), [])

    def test_crosses_languages(self):
        py = self.write("caller.py", "def run():\n    return sharedName()\n")
        ts = self.write("impl.ts", "function sharedName(): number {\n  return 1;\n}\n")
        gaps = self.index([py, ts]).gaps([py])
        self.assertEqual([g.rel_path for g in gaps], [ts])

    def test_unparseable_and_unsupported_files_do_not_break_the_index(self):
        caller = self.write("caller.py", "def run():\n    return helper()\n")
        helper = self.write("helper.py", "def helper():\n    return 1\n")
        broken = self.write("broken.py", "def (((\n")
        data = self.write("notes.txt", "helper helper helper\n")
        gaps = self.index([caller, helper, broken, data]).gaps([caller])
        self.assertEqual([g.rel_path for g in gaps], [helper])

    def test_missing_file_is_skipped(self):
        caller = self.write("caller.py", "def run():\n    return helper()\n")
        gaps = self.index([caller, f"/{self.name}/gone.py"]).gaps([caller])
        self.assertEqual(gaps, [])

    def test_an_index_that_parsed_nothing_reports_itself_unusable(self):
        """ "No gaps" and "could not look" must not render identically.

        Every tagger call raising - a broken tree-sitter install, say - produced an
        empty gap list, which reads as "your selection is closed".
        """

        class BrokenTagger:
            def extract_definitions(self, source):
                raise RuntimeError("no parser")

            def extract_references(self, source):
                raise RuntimeError("no parser")

        caller = self.write("caller.py", "def run():\n    return helper()\n")
        index = SymbolIndex.create(BrokenTagger(), self.root, [caller])
        self.assertEqual(index.gaps([caller]), [])
        self.assertTrue(index.unusable)

    def test_a_working_index_is_not_unusable(self):
        caller = self.write("caller.py", "def run():\n    return helper()\n")
        self.assertFalse(self.index([caller]).unusable)

    def test_an_empty_universe_is_not_unusable(self):
        self.assertFalse(SymbolIndex.create(None, self.root, []).unusable)

    def test_empty_selection_has_no_gaps(self):
        caller = self.write("caller.py", "def run():\n    return helper()\n")
        self.assertEqual(self.index([caller]).gaps([]), [])


if __name__ == "__main__":
    unittest.main()
