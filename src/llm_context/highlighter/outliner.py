from dataclasses import dataclass
from typing import Optional

from llm_context.highlighter.parser import Source
from llm_context.highlighter.tagger import ASTBasedTagger, DefRef, Tag
from llm_context.project_settings import ProjectSettings


@dataclass(frozen=True)
class OutlineFormatter:
    code_lines: list[str]
    lines_of_interest: list[int]
    show_lines: list[int]

    def to_formatted_string(self) -> str:
        return "".join(self.format_line(line, i) for i, line in enumerate(self.code_lines))

    def format_line(self, line_content: str, i: int) -> str:
        is_line_of_interest = i in self.lines_of_interest
        should_show_line = i in self.show_lines
        if should_show_line:
            line_prefix = "█" if is_line_of_interest else "│"
            return f"{line_prefix}{line_content}\n"
        else:
            return "⋮...\n" if i == 0 or i - 1 in self.show_lines else ""


@dataclass(frozen=True)
class Outliner:
    source: Source
    lines_of_interest: list[int]

    @staticmethod
    def create(file_tags: list[Tag], code: str) -> Optional["Outliner"]:
        if not file_tags:
            return None
        rel_path = file_tags[0].rel_path
        lines_of_interest = [tag.start.ln for tag in file_tags]
        source = Source(rel_path=rel_path, code=code)
        return Outliner(source, lines_of_interest)

    def to_highlights(self) -> dict[str, str]:
        code_lines = self.source.code.split("\n")
        highlighter = OutlineFormatter(
            code_lines=code_lines,
            lines_of_interest=sorted(self.lines_of_interest),
            show_lines=sorted(set(self.lines_of_interest)),
        )
        highlights = highlighter.to_formatted_string()
        return {"rel_path": self.source.rel_path, "highlights": highlights}


@dataclass(frozen=True)
class Outlines:
    defs: list[list[Tag]]
    source_set: list[Source]

    @staticmethod
    def create(source_set: list[Source]) -> "Outlines":
        extractor = ASTBasedTagger.create()
        def_refs = [DefRef.create(extractor, source) for source in source_set]
        defs = [def_ref.defs for def_ref in def_refs]
        return Outlines(defs, source_set)

    def to_code_outlines(self) -> list[dict[str, str]]:
        code_outlines = []
        for tags, source in zip(self.defs, self.source_set):
            if tags:
                outliner = Outliner.create(tags, source.code)
                if outliner:
                    code_outlines.append(outliner.to_highlights())
        return code_outlines


def generate_outlines(source_set: list[Source]) -> list[dict[str, str]]:
    return Outlines.create(source_set).to_code_outlines()
