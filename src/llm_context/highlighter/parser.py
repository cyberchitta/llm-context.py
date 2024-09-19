import warnings
from dataclasses import dataclass
from typing import NamedTuple

from tree_sitter import Language, Parser, Tree
from tree_sitter_languages import get_language, get_parser

from llm_context.highlighter.language_mapping import TagQuery, to_language

warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")


class Source(NamedTuple):
    rel_path: str
    code: str


@dataclass(frozen=True)
class AST:
    language_name: str
    language: Language
    parser: Parser
    tree: Tree
    rel_path: str

    @staticmethod
    def create_from_code(source: Source) -> "AST":
        language_name = to_language(source.rel_path)
        assert language_name, f"Unsupported language: {source.rel_path}"
        language = get_language(language_name)
        parser = get_parser(language_name)
        tree = parser.parse(bytes(source.code, "utf-8"))
        return AST(language_name, language, parser, tree, source.rel_path)

    def get_tag_query(self) -> str:
        return TagQuery().get_query(self.language_name)

    def captures(self, query_scm: str) -> list:
        query = self.language.query(query_scm)
        return query.captures(self.tree.root_node)
