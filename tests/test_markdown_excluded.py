import unittest

from llm_context.excerpters.markdown import Markdown
from llm_context.excerpters.parser import Source


class TestMarkdownExcluded(unittest.TestCase):
    """`lc-missing -e` must work on markdown files.

    `_collect_excluded` iterated the query matches as a dict while the rest of the
    module iterates them as a list of tuples, so every -e request against a markdown
    file raised AttributeError.
    """

    SOURCE = Source(
        "doc.md",
        "# Heading\n\nA paragraph that is not a heading.\n\n## Another\n\nMore prose here.\n",
    )

    def test_excluded_returns_content_without_crashing(self):
        result = Markdown({"with-code-blocks": False}).excluded([self.SOURCE])
        self.assertEqual(len(result), 1)
        self.assertIn("omitted_content", result[0].sections)
        self.assertIn("paragraph", result[0].sections["omitted_content"])

    def test_excluded_ignores_non_markdown(self):
        self.assertEqual(Markdown({}).excluded([Source("a.py", "x = 1\n")]), [])

    def test_excluded_handles_no_sources(self):
        self.assertEqual(Markdown({}).excluded([]), [])


if __name__ == "__main__":
    unittest.main()
