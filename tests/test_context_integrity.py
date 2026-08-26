import tempfile
import unittest
from pathlib import Path

from jinja2 import Environment, FileSystemLoader  # type: ignore

from llm_context import lc_resources
from llm_context.overviews import get_full_overview
from llm_context.state import AllSelections, FileSelection

TEMPLATES_PATH = Path(lc_resources.__file__).parent / "templates"


class TestNeedsSelection(unittest.TestCase):
    """A rule with no usable stored selection must be detectable.

    `get_selection` fabricates an empty FileSelection on a miss, which used to make
    'never selected' indistinguishable from 'selected nothing' - so `lc-context -r`
    on a fresh rule emitted a context with no file content at all.
    """

    def test_unknown_rule_needs_selection(self):
        selections = AllSelections.create_empty()
        self.assertTrue(selections.needs_selection("tmp-prm-fresh"))

    def test_stored_selection_with_files_does_not_need_selection(self):
        selections = AllSelections.create_empty().with_selection(
            FileSelection.create("tmp-prm-x", ["/proj/a.py"], [])
        )
        self.assertFalse(selections.needs_selection("tmp-prm-x"))

    def test_excerpted_only_selection_does_not_need_selection(self):
        selections = AllSelections.create_empty().with_selection(
            FileSelection.create("tmp-prm-x", [], ["/proj/a.py"])
        )
        self.assertFalse(selections.needs_selection("tmp-prm-x"))

    def test_stored_but_empty_selection_needs_selection(self):
        """State files poisoned by the old behaviour must self-heal."""
        selections = AllSelections.create_empty().with_selection(
            FileSelection.create("tmp-prm-x", [], [])
        )
        self.assertTrue(selections.needs_selection("tmp-prm-x"))


class TestOverviewCounts(unittest.TestCase):
    """The overview must report how much it actually included."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ["a.py", "b.py", "c.py", "d.py"]:
            (self.root / name).write_text("x = 1\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_counts_included_and_excluded(self):
        full = [str(self.root / "a.py")]
        result = get_full_overview(self.root, full, [], [])
        self.assertEqual(result.listed_count, 4)
        self.assertEqual(result.excluded_count, 3)

    def test_no_selection_marks_everything_excluded(self):
        result = get_full_overview(self.root, [], [], [])
        self.assertEqual(result.listed_count, 4)
        self.assertEqual(result.excluded_count, 4)

    def test_empty_project_is_not_a_crash(self):
        with tempfile.TemporaryDirectory() as empty:
            result = get_full_overview(Path(empty), [], [], [])
            self.assertEqual(result.listed_count, 0)
            self.assertEqual(result.excluded_count, 0)


class TestOverviewTemplate(unittest.TestCase):
    """The generated context must never claim to be complete.

    It cannot be: the file listing is filtered by the repo's .gitignore files and by
    the rule's own overview ignores before anything can even be marked excluded, and
    selection is the entire point of the tool. A reader that believes the claim stops
    asking for files it needs.
    """

    def render(self, **overrides):
        context = {
            "project_name": "proj",
            "context_timestamp": 1234.5,
            "abs_root_path": "/tmp/proj",
            "overview": "TREE",
            "overview_mode": "full",
            "full_count": 3,
            "outlined_count": 1,
            "excerpted_count": 2,
            "excluded_count": 40,
            "excerpts": True,
            "with_tools": True,
            "sample_requested_files": ["/proj/x.py"],
            "sample_excluded_files": ["/proj/y.py"],
        }
        context.update(overrides)
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_PATH)))
        return env.get_template("lc/overview.j2").render(**context)

    def test_never_claims_completeness(self):
        for mode in ["full", "focused"]:
            for with_tools in [True, False]:
                rendered = self.render(overview_mode=mode, with_tools=with_tools).upper()
                self.assertNotIn("COMPLETE PROJECT CONTEXT", rendered)
                self.assertNotIn("NO NEED TO REQUEST", rendered)
                self.assertNotIn("COMPREHENSIVE VIEW", rendered)

    def test_states_that_the_view_is_partial(self):
        self.assertIn("partial view", self.render())

    def test_warns_that_the_listing_is_itself_filtered(self):
        rendered = self.render()
        self.assertIn(".gitignore", rendered)
        self.assertIn("do not appear below at all", rendered)

    def test_reports_actual_counts(self):
        rendered = self.render(full_count=3, outlined_count=1, excerpted_count=2, excluded_count=40)
        self.assertIn("**3**", rendered)
        self.assertIn("**1**", rendered)
        self.assertIn("**2**", rendered)
        self.assertIn("**40**", rendered)

    def test_an_empty_pack_says_zero_rather_than_claiming_content(self):
        rendered = self.render(full_count=0, outlined_count=0, excerpted_count=0, excluded_count=40)
        self.assertIn("**0** file(s) included in full", rendered)
        self.assertNotIn("COMPLETE PROJECT CONTEXT", rendered.upper())


class TestCallbackInstructions(unittest.TestCase):
    """The commands a pack tells its reader to run must be real commands.

    The pack used to emit `lc-changed "<root>" <rule> <ts>` (lc-changed takes no
    arguments at all) and an lc_changed tool call carrying a `rule_name` field the
    tool does not accept.
    """

    def render(self, **overrides):
        context = {
            "project_name": "proj",
            "rule_name": "tmp-prm-task",
            "context_timestamp": 1234.5,
            "abs_root_path": "/tmp/proj",
            "overview": "TREE",
            "overview_mode": "full",
            "full_count": 3,
            "outlined_count": 1,
            "excerpted_count": 1,
            "excluded_count": 40,
            "excerpts": True,
            "with_tools": True,
            "consumer": "mcp",
            "sample_requested_files": ["/proj/x.py"],
            "sample_excluded_files": ["/proj/y.py"],
            "sample_outlined_file": "/proj/outlined.py",
            "sample_excerpted_file": "/proj/excerpted.md",
        }
        context.update(overrides)
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_PATH)))
        return env.get_template("lc/overview.j2").render(**context)

    def test_never_emits_lc_changed_with_arguments(self):
        for kwargs in [{}, {"consumer": "cli"}, {"with_tools": False}]:
            rendered = self.render(**kwargs)
            for line in rendered.splitlines():
                if "lc-changed" in line and line.strip().startswith("lc-changed"):
                    self.assertEqual(line.strip(), "lc-changed", "lc-changed takes no arguments")

    def test_mcp_change_call_has_no_rule_name(self):
        rendered = self.render(consumer="mcp")
        after = rendered.split("lc-changed tool", 1)
        self.assertEqual(len(after), 2, "mcp rendering should name the lc-changed tool")
        self.assertNotIn("rule_name", after[1].split("```")[1])

    def test_agent_rendering_gives_runnable_shell_commands(self):
        rendered = self.render(consumer="cli")
        self.assertIn("Run these yourself", rendered)
        self.assertIn("lc-missing -f", rendered)
        self.assertNotIn("the user should run", rendered)
        self.assertNotIn('"param_type"', rendered)

    def test_agent_examples_name_real_outlined_and_excerpted_files(self):
        rendered = self.render(consumer="cli")
        self.assertIn('lc-missing -i "[[\\"/proj/outlined.py\\"', rendered)
        self.assertIn('lc-missing -e "[\\"/proj/excerpted.md\\"]"', rendered)

    def test_human_rendering_addresses_the_user(self):
        rendered = self.render(with_tools=False)
        self.assertIn("Ask the user to run", rendered)
        self.assertNotIn('"param_type"', rendered)

    def test_mcp_rendering_keeps_the_tool_form(self):
        rendered = self.render(consumer="mcp")
        self.assertIn('"param_type"', rendered)
        self.assertNotIn("Run these yourself", rendered)


if __name__ == "__main__":
    unittest.main()
