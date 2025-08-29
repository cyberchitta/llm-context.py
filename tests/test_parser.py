import pytest

from llm_context.highlighter.parser import AST, ASTFactory, Source
from llm_context.highlighter.tagger import ASTBasedTagger, Definition, FileTags, Position, Tag


@pytest.fixture
def sample_ast():
    code = """
class TestClass:
    def test_method(self):
        pass

def test_function():
    obj = TestClass()
    obj.test_method()
    
test_function()
"""
    source = Source(rel_path="test.py", code=code)
    ast_factory = ASTFactory.create()
    return ast_factory.create_from_code(source)


@pytest.fixture
def sample_defref():
    code = """
class TestClass:
    def test_method(self):
        pass

def test_function():
    obj = TestClass()
    obj.test_method()
    
test_function()
"""
    source = Source(rel_path="test.py", code=code)
    ast_factory = ASTFactory.create()
    workspace_path = "/fake/workspace/path"
    tagger = ASTBasedTagger.create(workspace_path, ast_factory)
    return FileTags.create(tagger, source)


def test_ast_creation(sample_ast):
    assert sample_ast is not None
    assert sample_ast.language_name == "python"


def test_ast_captures(sample_ast):
    captures = sample_ast.tag_matches()
    assert len(captures) > 0


def test_defref_creation(sample_defref):
    assert sample_defref is not None
    assert sample_defref.rel_path == "test.py"


def test_defref_contents(sample_defref):
    defs = sample_defref.definitions
    assert len(defs) >= 2
    class_def = next((d for d in defs if d.name and d.name.text == "TestClass"), None)
    func_def = next((d for d in defs if d.name and d.name.text == "test_function"), None)
    assert class_def is not None, "TestClass definition not found"
    assert func_def is not None, "test_function definition not found"
    assert class_def.name is not None
    assert class_def.name.text == "TestClass"
    if func_def.name:
        assert func_def.name.text == "test_function"


def test_defref_positions(sample_defref):
    defs = sample_defref.definitions
    for defn in defs:
        assert defn.begin.ln >= 0
        assert defn.begin.col >= 0
        assert defn.end.ln >= defn.begin.ln
        assert defn.start >= 0
        assert defn.finish > defn.start
