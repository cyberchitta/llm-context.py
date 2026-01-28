from dataclasses import dataclass
from importlib import resources
from typing import Any, Optional, cast

from tree_sitter import Node

from llm_context.excerpters.base import Excerpt, Excerpter, Excerpts, Excluded
from llm_context.excerpters.language_mapping import to_language
from llm_context.excerpters.parser import ASTFactory, Source


@dataclass(frozen=True)
class ContentRange:
    start_line: int
    end_line: int
    node_type: str


@dataclass(frozen=True)
class Markdown(Excerpter):
    config: dict[str, Any]

    def excerpt(self, sources: list[Source]) -> Excerpts:
        if not sources:
            return Excerpts([], {})
        excerpts = [
            self._excerpt_source(source)
            for source in sources
            if to_language(source.rel_path) == "markdown"
        ]
        return Excerpts(excerpts, {"sample_definitions": []})

    def excluded(self, sources: list[Source]) -> list[Excluded]:
        if not sources:
            return []
        results = []
        for source in sources:
            if to_language(source.rel_path) != "markdown":
                continue
            excluded_content = self._collect_excluded(source)
            if excluded_content:
                results.append(
                    Excluded(
                        {"omitted_content": excluded_content},
                        {"file": source.rel_path},
                    )
                )
        return results

    def _excerpt_source(self, source: Source) -> Excerpt:
        ast = ASTFactory.create().create_from_code(source)
        included_ranges = self._get_included_ranges(ast, source)
        content = self._format_content(source.content, included_ranges)
        return Excerpt(source.rel_path, content, self._metadata())

    def _get_included_ranges(self, ast: Any, source: Source) -> set[int]:
        query_str = self._get_query()
        matches = ast.match(query_str)
        included_lines: set[int] = set()
        for _, captures in matches:
            for capture_name, nodes in captures.items():
                node_type = self._map_capture_to_type(capture_name)
                if self._should_include(node_type):
                    for node in nodes:
                        for line_num in range(node.start_point[0], node.end_point[0] + 1):
                            included_lines.add(line_num)
        return included_lines

    def _format_content(self, content: str, included_line_set: set[int]) -> str:
        lines = content.splitlines()
        result: list[str] = []
        last_included_index = -2
        for i, line in enumerate(lines):
            is_included = i in included_line_set
            if is_included:
                if i - last_included_index > 2 and result:
                    result.append("⋮...")
                result.append(line)
                last_included_index = i
        if result and last_included_index < len(lines) - 2:
            result.append("⋮...")
        return "\n".join(result)

    def _collect_excluded(self, source: Source) -> str:
        ast = ASTFactory.create().create_from_code(source)
        matches = ast.match(self._get_query())
        included_ranges: set[tuple[int, int]] = set()
        for _, captures in matches.items():
            for capture_name, nodes in captures.items():
                node_type = self._map_capture_to_type(capture_name)
                if self._should_include(node_type):
                    for node in nodes:
                        included_ranges.add((node.start_point[0], node.end_point[0]))
        excluded_paras = []
        for _, captures in matches.items():
            if "content.paragraph" in captures:
                for node in captures["content.paragraph"]:
                    node_range = (node.start_point[0], node.end_point[0])
                    if node_range not in included_ranges:
                        text = self._node_text(node, source.content)
                        if text.strip():
                            excluded_paras.append(text)
        return "\n\n".join(excluded_paras[:3]) if excluded_paras else ""

    def _map_capture_to_type(self, capture_name: str) -> str:
        mapping = {
            "heading.atx": "heading",
            "heading.setext": "heading",
            "code.fenced": "code_block",
            "code.indented": "code_block",
            "list.item": "list_item",
            "table.pipe": "table",
            "quote.block": "blockquote",
            "break.thematic": "thematic_break",
            "content.paragraph": "paragraph",
        }
        return mapping.get(capture_name, "")

    def _should_include(self, node_type: str) -> bool:
        config_map = {
            "heading": True,
            "code_block": cast(bool, self.config.get("with-code-blocks", True)),
            "list_item": cast(bool, self.config.get("with-lists", True)),
            "table": cast(bool, self.config.get("with-tables", True)),
            "blockquote": cast(bool, self.config.get("with-blockquotes", True)),
            "thematic_break": cast(bool, self.config.get("with-thematic-breaks", True)),
            "paragraph": False,
        }
        return config_map.get(node_type, False)

    def _get_query(self) -> str:
        return resources.files("llm_context.excerpters.ts-qry").joinpath("markdown.scm").read_text()

    def _node_text(self, node: Node, content: str) -> str:
        return content[node.start_byte : node.end_byte]

    def _metadata(self) -> dict[str, Any]:
        included = [
            k.replace("with-", "") for k, v in self.config.items() if isinstance(v, bool) and v
        ]
        return {
            "processor_type": "markdown",
            "included_elements": included,
        }
