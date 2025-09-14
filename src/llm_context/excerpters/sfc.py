from dataclasses import dataclass
from importlib import resources
from typing import Any, Optional, cast

from tree_sitter import Query, QueryCursor

from llm_context.excerpters.base import Excerpt, Excerpter, Excerpts, Excluded
from llm_context.excerpters.language_mapping import to_language
from llm_context.excerpters.parser import ASTFactory, Source


@dataclass(frozen=True)
class SfcSection:
    section_type: str  # "script", "style", "template"
    start_line: int
    end_line: int
    content: str
    attributes: dict[str, str]  # e.g., {"lang": "typescript"}


@dataclass(frozen=True)
class Sfc(Excerpter):
    config: dict[str, Any]

    def excerpt(self, sources: list[Source]) -> Excerpts:
        if not sources:
            return Excerpts([], {"sample_definitions": []})
        results = []
        for source in sources:
            language = to_language(source.rel_path)
            if language not in ["svelte", "vue"]:
                continue
            sections = self._parse_sfc_sections(source, language)
            excerpted_content = self._create_excerpt_content(source, sections)
            if excerpted_content:
                result = Excerpt(
                    source.rel_path,
                    excerpted_content,
                    {
                        "processor_type": "sfc-excerpter",
                        "sections_included": self._get_included_section_types(),
                        "language": language,
                    },
                )
                results.append(result)
        return Excerpts(results, {"sample_definitions": []})

    def excluded(self, sources: list[Source]) -> list[Excluded]:
        excluded_results = []
        for source in sources:
            language = to_language(source.rel_path)
            if language not in ["svelte", "vue"]:
                continue
            sections = self._parse_sfc_sections(source, language)
            excluded_sections = {}
            for section in sections:
                if not self._should_include_section(section.section_type):
                    excluded_sections[section.section_type] = section.content
            if excluded_sections:
                excluded_results.append(
                    Excluded(excluded_sections, {"language": language, "file": source.rel_path})
                )
        return excluded_results

    def _parse_sfc_sections(self, source: Source, language: str) -> list[SfcSection]:
        ast_factory = ASTFactory.create()
        ast = ast_factory.create_from_code(source)
        queries = self._get_sfc_queries(language)
        query = Query(ast.language, queries)
        cursor = QueryCursor(query)
        matches = cursor.matches(ast.tree.root_node)
        sections = []
        seen = set()
        for match_id, captures in matches:
            for capture_name, nodes in captures.items():
                if capture_name == "injection.content":
                    node_list = nodes if isinstance(nodes, list) else [nodes]
                    for node in node_list:
                        parent_node = node.parent
                        if parent_node:
                            section_type = self._get_section_type_from_node(parent_node)
                            if section_type:
                                start_byte = parent_node.start_byte
                                end_byte = parent_node.end_byte
                                key = (section_type, start_byte, end_byte)
                                if key not in seen:
                                    seen.add(key)
                                    sections.append(
                                        SfcSection(
                                            section_type=section_type,
                                            start_line=parent_node.start_point[0],
                                            end_line=parent_node.end_point[0],
                                            content=source.content[start_byte:end_byte],
                                            attributes={},
                                        )
                                    )
        return sorted(sections, key=lambda s: s.start_line)

    def _get_section_type_from_node(self, node) -> Optional[str]:
        if hasattr(node, "type"):
            if node.type == "script_element":
                return "script"
            elif node.type == "style_element":
                return "style"
            elif node.type == "template_element":
                return "template"
        return None

    def _get_sfc_queries(self, language: str) -> str:
        query_file = f"{language}-injections.scm"
        return resources.files("llm_context.excerpters.ts-qry").joinpath(query_file).read_text()

    def _create_excerpt_content(self, source: Source, sections: list[SfcSection]) -> str:
        lines = source.content.split("\n")
        result_lines = []
        last_included_line = -1
        for section in sections:
            if last_included_line >= 0 and section.start_line > last_included_line + 1:
                if self.config.get("with-template", False):
                    gap_lines = lines[last_included_line + 1 : section.start_line]
                    result_lines.extend(gap_lines)
                else:
                    result_lines.append("⋮...")
            if self._should_include_section(section.section_type):
                section_lines = lines[section.start_line : section.end_line + 1]
                result_lines.extend(section_lines)
                last_included_line = section.end_line
            else:
                if section.start_line > last_included_line + 1:
                    result_lines.append(lines[section.start_line])
                result_lines.append("⋮...")
                if section.end_line < len(lines) - 1:
                    result_lines.append(lines[section.end_line])
                last_included_line = section.end_line
        if last_included_line < len(lines) - 1:
            if self.config.get("with-template", False):
                result_lines.extend(lines[last_included_line + 1 :])
            else:
                result_lines.append("⋮...")
        return "\n".join(result_lines)

    def _should_include_section(self, section_type: str) -> bool:
        if section_type == "script":
            return True
        elif section_type == "style":
            return cast(bool, self.config.get("with-style", False))
        elif section_type == "template":
            return cast(bool, self.config.get("with-template", False))
        return False

    def _get_included_section_types(self) -> list[str]:
        included = ["script"]
        if self.config.get("with-style", False):
            included.append("style")
        if self.config.get("with-template", False):
            included.append("template")
        return included
