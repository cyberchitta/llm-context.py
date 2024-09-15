from dataclasses import dataclass, field
from typing import Optional

from llm_context.highlighter.parser import AST, Source
from llm_context.highlighter.tagger import ASTBasedTagger, DefRef, Tag


@dataclass(frozen=True)
class Scoper:
    num_lines: int
    scopes: list[list[list[int]]] = field(
        default_factory=lambda: [[[] for _ in range(1)] for _ in range(1)]
    )

    @staticmethod
    def create(num_lines: int) -> "Scoper":
        scopes: list[list[list[int]]] = [[] for _ in range(num_lines)]
        return Scoper(num_lines, scopes)

    def with_scope_data_initialized(self, node, depth: int = 0) -> "Scoper":
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        size = end_line - start_line
        if size:
            self.scopes[start_line].append([size, start_line, end_line])
        for child in node.children:
            self.with_scope_data_initialized(child, depth + 1)
        return self

    def to_dominant_scopes(self, code_lines: list[str]) -> "Scopes":
        scopes = []
        for i in range(self.num_lines):
            scopes_i = sorted(self.scopes[i], key=lambda x: (x[0], x[1], x[2]))
            scopes.append(scopes_i[0][1:] if len(scopes_i) > 1 else [0, -1])
        scope_starts: list[set[int]] = [set() for _ in range(self.num_lines)]
        for start_line, end_line in scopes:
            for i in range(start_line, end_line + 1):
                scope_starts[i].add(start_line)
        return Scopes(code_lines, scope_starts)


@dataclass(frozen=True)
class Scopes:
    code_lines: list[str]
    scope_starts: list[set[int]]

    def parent_scopes(self, line_numbers: list[int]) -> set[int]:
        parent_scopes = set()
        for line_of_interest in line_numbers:
            parent_scopes.update(self.scope_starts[line_of_interest])
        return parent_scopes

    def to_code_highlighter(self, line_numbers: list[int]) -> "Highlighter":
        assert line_numbers
        parent_scopes = self.parent_scopes(line_numbers)
        all_lines = sorted(set(parent_scopes) | set(line_numbers))
        lines_of_interest = sorted(line_numbers)
        return Highlighter(self.code_lines, lines_of_interest, all_lines)


@dataclass(frozen=True)
class Highlighter:
    code_lines: list[str]
    lines_of_interest: list[int]
    show_lines: list[int]

    def with_small_gaps_closed(self) -> "Highlighter":
        closed_show = set()
        sorted_show = sorted(self.show_lines)
        for i in range(len(sorted_show) - 1):
            closed_show.add(sorted_show[i])
            if sorted_show[i + 1] - sorted_show[i] == 2:
                closed_show.add(sorted_show[i] + 1)
        if sorted_show:
            closed_show.add(sorted_show[-1])
        return Highlighter(self.code_lines, self.lines_of_interest, list(closed_show))

    def to_formatted_string(self) -> str:
        return "".join(self.format_line(line, i) for i, line in enumerate(self.code_lines))

    def format_line(self, line_content: str, i: int) -> str:
        is_line_of_interest = i in self.lines_of_interest
        should_show_line = i in self.show_lines
        if should_show_line:
            line_prefix = "█" if is_line_of_interest else "│"
            return f"{line_prefix}{line_content}\n"
        return "⋮...\n" if i == 0 or i - 1 in self.show_lines else ""


@dataclass(frozen=True)
class TagProcessor:
    source: Source
    lines_of_interest: list[int]

    @staticmethod
    def create(file_tags: list[dict], code: str) -> "TagProcessor":
        rel_path = file_tags[0]["rel_path"]
        lines_of_interest = [tag["start"]["ln"] for tag in file_tags]
        assert lines_of_interest
        source = Source(rel_path=rel_path, code=code)
        return TagProcessor(source, lines_of_interest)

    def to_highlights(self) -> dict[str, str]:
        ast = AST.create_from_code(self.source)
        scope_tracker = Scoper.create(
            len(self.source.code.splitlines())
        ).with_scope_data_initialized(ast.tree.root_node)
        scopes = scope_tracker.to_dominant_scopes(self.source.code.splitlines())
        highlighter = scopes.to_code_highlighter(self.lines_of_interest)
        highlights = highlighter.with_small_gaps_closed().to_formatted_string()
        return {"rel_path": self.source.rel_path, "highlights": highlights}


@dataclass(frozen=True)
class Highlights:
    tags: list[list[Tag]]
    source_set: list[Source]

    @staticmethod
    def create(source_set: list[Source]) -> "Highlights":
        extractor = ASTBasedTagger.create()
        def_refs = [DefRef.create(extractor, source) for source in source_set]
        tags = [def_ref.defs for def_ref in def_refs]
        return Highlights(tags, source_set)

    def to_code_highlights(self) -> list[dict[str, str]]:
        code_highlights = []
        for tags, source in zip(self.tags, self.source_set):
            if tags:
                tag_processor = TagProcessor(source, [tag.start.ln for tag in tags])
                highlights = tag_processor.to_highlights()
                if highlights:
                    code_highlights.append(highlights)
        return code_highlights


def generate_highlights(source_set: list[Source]) -> Optional[list[dict[str, str]]]:
    highlights = Highlights.create(source_set)
    return highlights.to_code_highlights() if highlights else None
