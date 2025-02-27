import warnings
from dataclasses import dataclass
from typing import NamedTuple, cast

from tree_sitter import Language, Parser, Tree  # type: ignore

from llm_context.highlighter.language_mapping import to_language

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
class TagQueryFactory:
    query_cache: dict[str, str]

    @staticmethod
    def create() -> "TagQueryFactory":
        return TagQueryFactory({})

    def get_tag_query(self, language: str) -> str:
        if language not in self.query_cache:
            from llm_context.highlighter.language_mapping import TagQuery

            self.query_cache[language] = TagQuery().get_query(language)
        return self.query_cache[language]


@dataclass(frozen=True)
class ASTFactory:
    parser_factory: ParserFactory
    tagqry_factory: TagQueryFactory

    @staticmethod
    def create():
        return ASTFactory(ParserFactory.create(), TagQueryFactory.create())

    def create_from_code(self, source: Source) -> "AST":
        language_name = to_language(source.rel_path)
        assert language_name, f"Unsupported language: {source.rel_path}"
        language = self.parser_factory.get_language(language_name)
        parser = self.parser_factory.get_parser(language_name)
        tree = parser.parse(bytes(source.code, "utf-8"))
        return AST(language_name, language, parser, tree, self.tagqry_factory, source.rel_path)


@dataclass(frozen=True)
class AST:
    language_name: str
    language: Language
    parser: Parser
    tree: Tree
    tag_query_factory: TagQueryFactory
    rel_path: str

    def get_tag_query(self) -> str:
        return self.tag_query_factory.get_tag_query(self.language_name)

    def captures(self, query_scm: str) -> list[tuple]:
        query = self.language.query(query_scm)
        matches = query.matches(self.tree.root_node)
        captures = []
        for _, capture_dict in matches:
            for tag_name, nodes in capture_dict.items():
                for node in nodes:
                    captures.append((node, tag_name))
        return captures
