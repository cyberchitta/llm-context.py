import warnings
from dataclasses import dataclass
from typing import Any, NamedTuple, cast

from tree_sitter import Language, Node, Parser, Tree  # type: ignore

from llm_context.highlighter.language_mapping import LangQuery, to_language

warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")


class Source(NamedTuple):
    rel_path: str
    code: str


@dataclass(frozen=True)
class ParserFactory:
    parser_cache: dict[str, tuple[Language, Parser]]

    @staticmethod
    def create() -> "ParserFactory":
        return ParserFactory({})

    def _create_tuple(self, language_name: str) -> tuple[Language, Parser]:
        from tree_sitter_language_pack import SupportedLanguage, get_language, get_parser

        language = get_language(cast(SupportedLanguage, language_name))
        parser = get_parser(cast(SupportedLanguage, language_name))
        return (language, parser)

    def get_tuple(self, language_name: str) -> tuple[Language, Parser]:
        if language_name not in self.parser_cache:
            self.parser_cache[language_name] = self._create_tuple(language_name)
        return self.parser_cache[language_name]

    def get_parser(self, language_name: str) -> Parser:
        return self.get_tuple(language_name)[1]

    def get_language(self, language_name: str) -> Language:
        return self.get_tuple(language_name)[0]


@dataclass(frozen=True)
class LangQueryFactory:
    tag_query_cache: dict[str, str]

    @staticmethod
    def create() -> "LangQueryFactory":
        return LangQueryFactory({})

    def get_tag_query(self, language: str) -> str:
        if language not in self.tag_query_cache:
            self.tag_query_cache[language] = LangQuery().get_tag_query(language)
        return self.tag_query_cache[language]


@dataclass(frozen=True)
class ASTFactory:
    parser_factory: ParserFactory
    lang_qry_factory: LangQueryFactory

    @staticmethod
    def create():
        return ASTFactory(ParserFactory.create(), LangQueryFactory.create())

    def create_from_code(self, source: Source) -> "AST":
        language_name = to_language(source.rel_path)
        assert language_name, f"Unsupported language: {source.rel_path}"
        language = self.parser_factory.get_language(language_name)
        parser = self.parser_factory.get_parser(language_name)
        tree = parser.parse(bytes(source.code, "utf-8"))
        return AST(language_name, language, parser, tree, self.lang_qry_factory, source.rel_path)


@dataclass(frozen=True)
class AST:
    language_name: str
    language: Language
    parser: Parser
    tree: Tree
    lang_qry_factory: LangQueryFactory
    rel_path: str

    def match(self, query_scm) -> list[tuple[int, dict[str, list[Node]]]]:
        query = self.language.query(query_scm)
        return query.matches(self.tree.root_node)

    def tag_matches(self) -> list[tuple[int, dict[str, list[Node]]]]:
        return self.match(self._get_tag_query())

    def _get_tag_query(self) -> str:
        return self.lang_qry_factory.get_tag_query(self.language_name)


@dataclass(frozen=True)
class ASTNode:
    node: Node

    @staticmethod
    def create(node: Node | None):
        return ASTNode(node) if node else None

    def to_definition(self, name: "ASTNode") -> dict[str, Any]:
        return {"type": self.node.type, "name": name.to_text(), **self.to_text()}

    def to_text(self) -> dict[str, Any]:
        text = self.node.text.decode("utf8") if self.node.text else ""
        return {"text": text, **self.to_pos_info()} if self.node else {}

    def to_pos_info(self) -> dict[str, Any]:
        return {
            "start_point": self.node.start_point,
            "end_point": self.node.end_point,
            "start_byte": self.node.start_byte,
            "end_byte": self.node.end_byte,
        }


def to_definition(match: tuple[int, dict[str, list[Any]]]) -> dict[str, Any]:
    _, captures = match
    def_capture = next((name for name in captures if name.startswith("definition.")), None)
    if not def_capture:
        return {}
    name_nodes: list[Node] = captures.get("name", [])
    name_node = ASTNode.create(name_nodes[0] if name_nodes else None)
    def_node = ASTNode.create(captures[def_capture][0])
    return cast(dict[str, Any], def_node.to_definition(name_node))
