import pytest

from llm_context.highlighter.parser import AST, Source
from llm_context.highlighter.tagger import ASTBasedTagger, DefRef, Position


@pytest.fixture
def sample_ast():
    source = Source(
        rel_path="test.py",
        code="""def test_function():
    pass
""",
    )
    ast = AST.create_from_code(source)
    return source, ast


@pytest.fixture
def sample_defref():
    source = Source(
        rel_path="test.py",
        code="""
class TestClass:
    def test_method(self):
        pass

def test_function():
    obj = TestClass()
    obj.test_method()
    
test_function()
""",
    )

    extractor = ASTBasedTagger.create()
    defref = DefRef.create(extractor, source)
    return source, defref


# AST Tests
def test_ast_creation(sample_ast):
    source, ast = sample_ast
    assert ast is not None
    assert ast.rel_path == "test.py"
    assert ast.language is not None
    assert ast.parser is not None
    assert ast.tree is not None


def test_ast_captures(sample_ast):
    source, ast = sample_ast
    query = "(function_definition name: (identifier) @function.name)"
    captures = ast.captures(query)
    assert len(captures) == 1
    assert captures[0][1] == "function.name"
    assert captures[0][0].text == b"test_function"


# DefRef Tests
def test_defref_creation(sample_defref):
    source, defref = sample_defref

    assert defref is not None
    assert defref.rel_path == "test.py"
    assert len(defref.all) > 0
    assert len(defref.defs) > 0
    assert len(defref.refs) > 0


def test_defref_contents(sample_defref):
    source, defref = sample_defref

    # Check definitions
    assert any(tag for tag in defref.defs if tag.text == "TestClass" and tag.kind == "def")
    assert any(tag for tag in defref.defs if tag.text == "test_method" and tag.kind == "def")
    assert any(tag for tag in defref.defs if tag.text == "test_function" and tag.kind == "def")

    # Check references
    assert any(tag for tag in defref.refs if tag.text == "TestClass" and tag.kind == "ref")
    assert any(tag for tag in defref.refs if tag.text == "test_method" and tag.kind == "ref")
    assert any(tag for tag in defref.refs if tag.text == "test_function" and tag.kind == "ref")


def test_defref_positions(sample_defref):
    source, defref = sample_defref

    # Check positions of definitions
    test_class_def = next(tag for tag in defref.defs if tag.text == "TestClass")
    assert test_class_def.start == Position(1, 6)  # Line 2 becomes 1 in zero-indexing

    test_method_def = next(tag for tag in defref.defs if tag.text == "test_method")
    assert test_method_def.start == Position(2, 8)  # Line 3 becomes 2

    test_function_def = next(tag for tag in defref.defs if tag.text == "test_function")
    assert test_function_def.start == Position(5, 4)  # Line 6 becomes 5

    # Check positions of references
    test_class_ref = next(tag for tag in defref.refs if tag.text == "TestClass")
    assert test_class_ref.start == Position(6, 10)  # Line 7 becomes 6

    test_method_ref = next(tag for tag in defref.refs if tag.text == "test_method")
    assert test_method_ref.start == Position(7, 8)  # Line 8 becomes 7

    test_function_ref = next(tag for tag in defref.refs if tag.text == "test_function")
    assert test_function_ref.start == Position(9, 0)  # Line 10 becomes 9
