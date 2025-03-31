import random
from dataclasses import dataclass
from typing import Optional, cast

from llm_context.highlighter.parser import Source
from llm_context.highlighter.tagger import ASTBasedTagger, Definition, FileTags, Tag


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
    def create(file_tags: list[Definition], code: str) -> Optional["Outliner"]:
        if not file_tags:
            return None
        rel_path = file_tags[0].rel_path
        lines_of_interest = [tag.name.begin.ln if tag.name else tag.begin.ln for tag in file_tags]
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
    defs: list[list[Definition]]
    source_set: list[Source]

    @staticmethod
    def create(tagger: ASTBasedTagger, source_set: list[Source]) -> "Outlines":
        all_tags = [FileTags.create(tagger, source).definitions for source in source_set]
        return Outlines(all_tags, source_set)

    def to_code_outlines(self) -> list[dict[str, str]]:
        code_outlines = []
        for tags, source in zip(self.defs, self.source_set):
            if tags:
                outliner = Outliner.create(tags, source.code)
                if outliner:
                    code_outlines.append(outliner.to_highlights())
        return code_outlines

    def sample_definitions(self, max_samples: int = 2) -> list[tuple[str, str]]:
        files_with_defs = [
            (i, [t for t in tags if t.name and t.name.text])
            for i, tags in enumerate(self.defs)
            if any(t.name and t.name.text for t in tags)
        ]
        sampled = random.sample(files_with_defs, min(max_samples, len(files_with_defs)))
        return [
            (d.rel_path, cast(Tag, d.name).text)
            for _, defs in sampled
            for d in [random.choice(defs)]
        ]


def generate_outlines(
    tagger: ASTBasedTagger, source_set: list[Source]
) -> tuple[list[dict[str, str]], list[tuple[str, str]]]:
    outlines = Outlines.create(tagger, source_set)
    code_outlines = outlines.to_code_outlines()
    sample_definitions = outlines.sample_definitions()
    return code_outlines, sample_definitions
