from dataclasses import dataclass
from typing import NamedTuple, Optional, Protocol

from llm_context.highlighter.language_mapping import TagQuery, to_language
from llm_context.highlighter.parser import AST, Source
from llm_context.project_settings import ProjectSettings


class Position(NamedTuple):
    ln: int
    col: int


class Tag(NamedTuple):
    rel_path: str
    text: str
    kind: str
    start: Position
    end: Position


class TagExtractor(Protocol):
    workspace_path: str

    def extract_tags(self, source: Source) -> list[Tag]: ...


@dataclass(frozen=True)
class Tagger:
    ast: AST
    query_scm: str

    @staticmethod
    def create(ast: AST) -> "Tagger":
        return Tagger(ast, ast.get_tag_query())

    @staticmethod
    def _get_kind(tag: str) -> str:
        if tag.startswith("name.definition."):
            return "def"
        elif tag.startswith("name.reference."):
            return "ref"
        return ""

    def read(self) -> list[Tag]:
        return [
            Tag(
                self.ast.rel_path,
                node.text.decode(),
                self._get_kind(tag),
                Position(node.start_point[0], node.start_point[1]),
                Position(node.end_point[0], node.end_point[1]),
            )
            for node, tag in self.ast.captures(self.query_scm)
            if self._get_kind(tag)
        ]


@dataclass(frozen=True)
class ASTBasedTagger(TagExtractor):
    @staticmethod
    def create():
        return ASTBasedTagger()

    def extract_tags(self, source: Source) -> list[Tag]:
        ast = AST.create_from_code(source)
        return Tagger.create(ast).read()


@dataclass(frozen=True)
class DefRef:
    rel_path: str
    all: list[Tag]
    defs: list[Tag]
    refs: list[Tag]

    @staticmethod
    def create(extractor: TagExtractor, source: Source) -> "DefRef":
        tags = extractor.extract_tags(source)
        defs = [tag for tag in tags if tag.kind == "def"]
        refs = [tag for tag in tags if tag.kind == "ref"]
        return DefRef(source.rel_path, tags, defs, refs)

    @staticmethod
    def create_each(extractor: TagExtractor, sources: list[Source]) -> list["DefRef"]:
        return [DefRef.create(extractor, source) for source in sources]


class SymbolRegistry(NamedTuple):
    workspace_path: str
    rel_paths: set[str]
    defines: dict[str, set[str]]
    definitions: dict[str, set[Tag]]
    references: dict[str, list[str]]
    identifiers: list[str]


@dataclass(frozen=True)
class DefRefs:
    workspace_path: str
    def_refs: list[DefRef]

    @staticmethod
    def create(teg_xtractor: TagExtractor, sources: list[Source]) -> Optional["DefRefs"]:
        def_refs = DefRef.create_each(teg_xtractor, sources)
        non_empty = [def_ref for def_ref in def_refs if def_ref.defs or def_ref.refs]
        if not non_empty:
            return None
        return DefRefs(teg_xtractor.workspace_path, non_empty)

    def create_tags(self) -> Optional["SymbolRegistry"]:
        defines: dict[str, set[str]] = {}
        definitions: dict[str, set[Tag]] = {}
        references: dict[str, list[str]] = {}

        for def_ref in self.def_refs:
            for def_ in def_ref.defs:
                defines.setdefault(def_.text, set()).add(def_ref.rel_path)
                definitions.setdefault(f"{def_ref.rel_path},{def_.text}", set()).add(def_)

            for ref in def_ref.refs:
                references.setdefault(ref.text, []).append(def_ref.rel_path)

        if not references:
            for key, value in defines.items():
                references[key] = list(value)

        rel_paths = set([def_ref.rel_path for def_ref in self.def_refs])

        if not defines or not definitions or not references:
            return None

        identifiers = [key for key in defines.keys() if key in references]

        return SymbolRegistry(
            self.workspace_path, rel_paths, defines, definitions, references, identifiers
        )
