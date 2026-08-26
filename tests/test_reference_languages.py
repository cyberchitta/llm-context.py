"""Reference extraction across every language with a tag query.

`_tag_languages` lists 14 languages. Twelve of their tag queries carry
`@reference.*` captures; `c` and `cpp` carry only definitions. That split is
asserted here rather than left implicit, so adding reference captures to either
grammar fails the test that says it has none.
"""

import pytest

from llm_context.excerpters.language_mapping import _tag_languages
from llm_context.excerpters.parser import ASTFactory, Source
from llm_context.excerpters.tagger import ASTBasedTagger

# (language, extension, source, expected definition, expected referenced symbol)
WITH_REFERENCES = [
    (
        "csharp",
        "cs",
        "class Greeter {\n  public void Run() { Helper.Work(); }\n}\n",
        "Greeter",
        "Work",
    ),
    ("elisp", "el", "(defun my-run ()\n  (helper-work))\n", "my-run", "helper-work"),
    (
        "elixir",
        "ex",
        "defmodule Greeter do\n  def run do\n    Helper.work()\n  end\nend\n",
        "run",
        "work",
    ),
    (
        "elm",
        "elm",
        "module Main exposing (..)\n\nrun : Int\nrun =\n    helperWork 1\n",
        "run",
        "helperWork",
    ),
    (
        "go",
        "go",
        "package main\n\nfunc Run() int {\n\treturn HelperWork()\n}\n",
        "Run",
        "HelperWork",
    ),
    (
        "java",
        "java",
        "class Greeter {\n  void run() { Helper.work(); }\n}\n",
        "Greeter",
        "work",
    ),
    (
        "javascript",
        "js",
        "function run() {\n  return helperWork();\n}\n",
        "run",
        "helperWork",
    ),
    ("php", "php", "<?php\nfunction run() {\n  return helper_work();\n}\n", "run", "helper_work"),
    ("python", "py", "def run():\n    return helper_work()\n", "run", "helper_work"),
    ("ruby", "rb", "def run\n  helper_work\nend\n", "run", "helper_work"),
    ("rust", "rs", "fn run() -> u32 {\n    helper_work()\n}\n", "run", "helper_work"),
    (
        "typescript",
        "ts",
        "function run(): number {\n  return helperWork();\n}\n",
        "run",
        "helperWork",
    ),
]

DEFINITIONS_ONLY = [
    ("c", "c", "int run(void) {\n  return helper_work();\n}\n", "run"),
    ("cpp", "cpp", "int run() {\n  return helper_work();\n}\n", "run"),
]


def tagger():
    return ASTBasedTagger.create("/proj", ASTFactory.create())


def test_every_tag_language_is_covered():
    covered = {lang for lang, *_ in WITH_REFERENCES} | {lang for lang, *_ in DEFINITIONS_ONLY}
    assert covered == set(_tag_languages), (
        f"uncovered: {set(_tag_languages) - covered}; unknown: {covered - set(_tag_languages)}"
    )


@pytest.mark.parametrize("language,ext,code,definition,reference", WITH_REFERENCES)
def test_extracts_definitions_and_references(language, ext, code, definition, reference):
    source = Source(f"/proj/sample.{ext}", code)
    extractor = tagger()
    names = {d.name.text for d in extractor.extract_definitions(source) if d.name}
    assert definition in names, f"{language}: definitions were {names}"
    referenced = {r.name for r in extractor.extract_references(source)}
    assert reference in referenced, f"{language}: references were {referenced}"


@pytest.mark.parametrize("language,ext,code,definition,reference", WITH_REFERENCES)
def test_references_carry_a_kind_and_position(language, ext, code, definition, reference):
    references = tagger().extract_references(Source(f"/proj/sample.{ext}", code))
    assert references
    for ref in references:
        assert ref.rel_path == f"/proj/sample.{ext}"
        assert ref.kind
        assert ref.begin.ln >= 0


@pytest.mark.parametrize("language,ext,code,definition", DEFINITIONS_ONLY)
def test_definition_only_languages(language, ext, code, definition):
    """c and cpp tag queries have no @reference.* captures.

    If this fails because references appeared, the grammar gained them - move the
    language into WITH_REFERENCES rather than relaxing the assertion.
    """
    source = Source(f"/proj/sample.{ext}", code)
    extractor = tagger()
    names = {d.name.text for d in extractor.extract_definitions(source) if d.name}
    assert definition in names, f"{language}: definitions were {names}"
    assert extractor.extract_references(source) == []


@pytest.mark.parametrize("language,ext,code,definition,reference", WITH_REFERENCES)
def test_empty_source_yields_nothing(language, ext, code, definition, reference):
    assert tagger().extract_references(Source(f"/proj/empty.{ext}", "")) == []
