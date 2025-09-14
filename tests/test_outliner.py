import pytest

from llm_context.excerpters.code_outliner import CodeOutliner
from llm_context.excerpters.parser import ASTFactory, Source
from llm_context.excerpters.tagger import ASTBasedTagger


@pytest.fixture
def tagger():
    workspace_path = "/fake/workspace/path"
    ast_factory = ASTFactory.create()
    return ASTBasedTagger.create(workspace_path, ast_factory)


@pytest.fixture
def sample_source():
    code = """
class TestClass:
    def test_method(self):
        pass

def test_function():
    pass
"""
    return Source(rel_path="test.py", content=code)


def test_code_outliner_integration(sample_source, tagger):
    """Test the complete code outlining functionality."""
    excerpter = CodeOutliner({"tagger": tagger})
    result = excerpter.excerpt([sample_source])
    assert len(result.excerpts) == 1
    assert result.excerpts[0].rel_path == "test.py"
    assert "class TestClass" in result.excerpts[0].content
    assert result.excerpts[0].metadata["processor_type"] == "code-outliner"
    assert "sample_definitions" in result.metadata
    assert isinstance(result.metadata["sample_definitions"], list)


def test_code_outliner_empty_sources(tagger):
    """Test handling of empty source list."""
    excerpter = CodeOutliner({"tagger": tagger})
    result = excerpter.excerpt([])
    assert len(result.excerpts) == 0
    assert result.metadata["sample_definitions"] == []


def test_code_outliner_unsupported_language(tagger):
    """Test handling of unsupported file types."""
    source = Source("test.txt", "some text content")
    excerpter = CodeOutliner({"tagger": tagger})
    result = excerpter.excerpt([source])
    assert len(result.excerpts) == 0
    assert result.metadata["sample_definitions"] == []


def test_code_outliner_multiple_sources(tagger):
    """Test processing multiple source files."""
    sources = [
        Source("file1.py", "def func1():\n    pass"),
        Source("file2.py", "class Class2:\n    def method2(self):\n        pass"),
        Source("file3.txt", "unsupported file"),
    ]
    excerpter = CodeOutliner({"tagger": tagger})
    result = excerpter.excerpt(sources)
    assert len(result.excerpts) == 2
    paths = {excerpt.rel_path for excerpt in result.excerpts}
    assert paths == {"file1.py", "file2.py"}
    for excerpt in result.excerpts:
        assert excerpt.metadata["processor_type"] == "code-outliner"


def test_code_outliner_no_definitions(tagger):
    """Test handling of code with no extractable definitions."""
    source = Source("empty.py", "# just a comment\nprint('hello')")
    excerpter = CodeOutliner({"tagger": tagger})
    result = excerpter.excerpt([source])
    assert isinstance(result.excerpts, list)
    assert result.metadata["sample_definitions"] == []
