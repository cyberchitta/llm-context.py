import pytest

from llm_context.highlighter.highlighter import generate_highlights
from llm_context.highlighter.outliner import Outliner, Outlines
from llm_context.highlighter.parser import Source
from llm_context.highlighter.tagger import Position, Tag


def test_outliner_line_numbering():
    source = Source(
        rel_path="test.txt",
        code="""line1
line2
function
line4
line5""",
    )
    tags = [
        Tag(
            rel_path="test.txt",
            text="function",
            kind="def",
            start=Position(2, 0),
            end=Position(2, 8),
        ),
    ]

    outliner = Outliner.create(tags, source.code)
    assert outliner is not None
    highlights = outliner.to_highlights()["highlights"]

    expected_output = """⋮...
█function
⋮...
"""
    assert highlights.strip() == expected_output.strip()


def test_outliner_first_line_highlighting():
    source = Source(
        rel_path="test.txt",
        code="""function
line2
line3
line4
line5""",
    )
    tags = [
        Tag(
            rel_path="test.txt",
            text="function",
            kind="def",
            start=Position(0, 0),  # This represents the first line in the file
            end=Position(0, 8),
        ),
    ]

    outliner = Outliner.create(tags, source.code)
    assert outliner is not None
    highlights = outliner.to_highlights()["highlights"]

    expected_output = """█function
⋮...
"""
    assert highlights.strip() == expected_output.strip()


@pytest.fixture
def sample_source():
    return Source(
        rel_path="test.py",
        code="""def test_function():
    pass

class TestClass:
    def test_method(self):
        return True

test_function()
TestClass().test_method()
""".strip(),
    )


def test_outliner_creation(sample_source):
    tags = [
        Tag(
            rel_path="test.py",
            text="test_function",
            kind="def",
            start=Position(0, 4),
            end=Position(0, 17),
        ),
        Tag(
            rel_path="test.py",
            text="TestClass",
            kind="def",
            start=Position(3, 6),
            end=Position(3, 15),
        ),
        Tag(
            rel_path="test.py",
            text="test_method",
            kind="def",
            start=Position(4, 8),
            end=Position(4, 19),
        ),
    ]
    outliner = Outliner.create(tags, sample_source.code)
    assert outliner is not None
    assert outliner.source.rel_path == "test.py"
    assert outliner.lines_of_interest == [
        0,
        3,
        4,
    ]  # These are now correct zero-indexed line numbers


def test_outliner_highlights(sample_source):
    tags = [
        Tag(
            rel_path="test.py",
            text="test_function",
            kind="def",
            start=Position(0, 4),
            end=Position(0, 17),
        ),
        Tag(
            rel_path="test.py",
            text="TestClass",
            kind="def",
            start=Position(3, 6),
            end=Position(3, 15),
        ),
        Tag(
            rel_path="test.py",
            text="test_method",
            kind="def",
            start=Position(4, 8),
            end=Position(4, 19),
        ),
    ]
    outliner = Outliner.create(tags, sample_source.code)
    highlights = outliner.to_highlights()

    expected_output = """█def test_function():
⋮...
█class TestClass:
█    def test_method(self):
⋮...
"""
    assert highlights["highlights"].strip() == expected_output.strip()


def test_generate_highlights(sample_source):
    highlights = generate_highlights([sample_source])

    assert highlights is not None
    assert len(highlights) == 1
    assert "rel_path" in highlights[0]
    assert "highlights" in highlights[0]
    assert highlights[0]["rel_path"] == "test.py"

    expected_highlights = """█def test_function():
⋮...
█class TestClass:
█    def test_method(self):
⋮...
"""
    assert highlights[0]["highlights"].strip() == expected_highlights.strip()
