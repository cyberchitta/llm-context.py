from dataclasses import dataclass
from typing import Any, NamedTuple, Optional, Protocol

from llm_context.highlighter.parser import ASTFactory, Source, to_definition


class Position(NamedTuple):
    ln: int
    col: int


@dataclass(frozen=True)
class Tag:
    text: str
    begin: Position
    end: Position
    start: int
    finish: int

    @staticmethod
    def create(node: dict[str, Any]) -> Optional["Tag"]:
        return (
            Tag(
                node["text"],
                Position(node["start_point"][0], node["start_point"][1]),
                Position(node["end_point"][0], node["end_point"][1]),
                node["start_byte"],
                node["end_byte"],
            )
            if node
            else None
        )


@dataclass(frozen=True)
class Definition:
    rel_path: str
    name: Tag | None
    text: str
    begin: Position
    end: Position
    start: int
    finish: int

    @staticmethod
    def create(rel_path: str, node: dict[str, Any]) -> "Definition":
        return Definition(
            rel_path,
            Tag.create(node["name"]),
            node["text"],
            Position(node["start_point"][0], node["start_point"][1]),
            Position(node["end_point"][0], node["end_point"][1]),
            node["start_byte"],
            node["end_byte"],
        )


class TagExtractor(Protocol):
    workspace_path: str

    def extract_definitions(self, source: Source) -> list[Definition]: ...


@dataclass(frozen=True)
class ASTBasedTagger(TagExtractor):
    workspace_path: str
    ast_factory: ASTFactory

    @staticmethod
    def create(workspace_path: str, ast_factory: ASTFactory) -> "ASTBasedTagger":
        return ASTBasedTagger(workspace_path, ast_factory)

    def extract_definitions(self, source: Source) -> list[Definition]:
        ast = self.ast_factory.create_from_code(source)
        return [
            Definition.create(ast.rel_path, defn)
            for defn in map(to_definition, ast.tag_matches())
            if defn
        ]


@dataclass(frozen=True)
class FileTags:
    rel_path: str
    definitions: list[Definition]

    @staticmethod
    def create(extractor: TagExtractor, source: Source) -> "FileTags":
        definitions = extractor.extract_definitions(source)
        return FileTags(source.rel_path, definitions)

    @staticmethod
    def create_each(extractor: TagExtractor, sources: list[Source]) -> list["FileTags"]:
        return [FileTags.create(extractor, source) for source in sources]


def find_definition(definitions, name):
    return [d.text for d in definitions if d.name and d.name.text == name]
