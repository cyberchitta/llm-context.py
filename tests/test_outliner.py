import pytest

from llm_context.excerpters.outliner import Outliner, generate_outlines
from llm_context.excerpters.parser import ASTFactory, Source
from llm_context.excerpters.tagger import ASTBasedTagger, Definition, Position, Tag


@pytest.fixture
def tagger():
    workspace_path = "/fake/workspace/path"
    ast_factory = ASTFactory.create()
    return ASTBasedTagger.create(workspace_path, ast_factory)


def test_outliner_line_numbering():
    code = "line1\nline2\nline3\nline4\nline5"
    lines_of_interest = [1, 3]  # zero-indexed, so lines 2 and 4
    source = Source(rel_path="test.py", code=code)
    outliner = Outliner(source, lines_of_interest)

    result = outliner.to_highlights()
    assert "█line2" in result["excerpts"]
    assert "█line4" in result["excerpts"]


def test_outliner_first_line_highlighting():
    code = "line1\nline2\nline3"
    lines_of_interest = [0]  # first line
    source = Source(rel_path="test.py", code=code)
    outliner = Outliner(source, lines_of_interest)

    result = outliner.to_highlights()
    assert "█line1" in result["excerpts"]


@pytest.fixture
def sample_source():
    code = """
class TestClass:
    def test_method(self):
        pass

def test_function():
    pass
"""
    return Source(rel_path="test.py", code=code)


@pytest.fixture
def sample_definitions(sample_source):
    class_def = Definition(
        rel_path=sample_source.rel_path,
        name=Tag("TestClass", Position(1, 6), Position(1, 15), 7, 16),
        text="class TestClass:",
        begin=Position(1, 0),
        end=Position(3, 12),
        start=1,
        finish=44,
    )

    method_def = Definition(
        rel_path=sample_source.rel_path,
        name=Tag("test_method", Position(2, 8), Position(2, 19), 27, 38),
        text="def test_method(self):",
        begin=Position(2, 4),
        end=Position(3, 12),
        start=23,
        finish=56,
    )
    return [class_def, method_def]


def test_outliner_creation(sample_source, sample_definitions):
    outliner = Outliner.create(sample_definitions, sample_source.code)
    assert outliner is not None
    assert outliner.source.rel_path == "test.py"
    assert len(outliner.lines_of_interest) == 2


def test_outliner_highlights(sample_source, sample_definitions):
    outliner = Outliner.create(sample_definitions, sample_source.code)
    highlights = outliner.to_highlights()

    assert highlights["rel_path"] == "test.py"
    assert "█class TestClass" in highlights["excerpts"]
    assert "█    def test_method" in highlights["excerpts"]


def test_generate_highlights(sample_source, tagger):
    defs = tagger.extract_definitions(sample_source)
    assert len(defs) > 0

    outlines, _ = generate_outlines(tagger, [sample_source])
    assert len(outlines) == 1
    assert outlines[0]["rel_path"] == "test.py"
    assert "class TestClass" in outlines[0]["excerpts"]
