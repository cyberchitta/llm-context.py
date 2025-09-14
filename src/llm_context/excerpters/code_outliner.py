import random
from dataclasses import dataclass
from typing import Any, Optional, cast

from llm_context.excerpters.base import Excerpt, Excerpter, Excerpts, Excluded
from llm_context.excerpters.language_mapping import to_language
from llm_context.excerpters.parser import Source
from llm_context.excerpters.tagger import ASTBasedTagger, Definition, FileTags, Tag


@dataclass(frozen=True)
class CodeOutliner(Excerpter):
    config: dict[str, Any]

    def excerpt(self, sources: list[Source]) -> Excerpts:
        if not sources:
            return self._empty_result()
        excerpts = []
        sample_definitions = []
        for source in sources:
            if self._should_process_source(source):
                excerpt = self._process_single_source(source)
                if excerpt:
                    excerpts.append(excerpt)
        tagger = self.config["tagger"]
        all_definitions = self._extract_all_definitions(sources, tagger)
        sample_definitions = self._generate_sample_definitions(all_definitions)
        return Excerpts(excerpts, {"sample_definitions": sample_definitions})

    def excluded(self, sources: list[Source]) -> list[Excluded]:
        return []

    def _should_process_source(self, source: Source) -> bool:
        return to_language(source.rel_path) is not None

    def _process_single_source(self, source: Source) -> Optional[Excerpt]:
        tagger = self.config["tagger"]
        definitions = tagger.extract_definitions(source)
        if not definitions:
            return None
        formatted_content = self._format_content(source, definitions)
        return Excerpt(source.rel_path, formatted_content, self._create_metadata())

    def _format_content(self, source: Source, definitions: list[Definition]) -> str:
        code_lines = source.content.split("\n")
        lines_of_interest = sorted(
            [tag.name.begin.ln if tag.name else tag.begin.ln for tag in definitions]
        )
        show_lines = sorted(set(lines_of_interest))
        formatted_lines = []
        for i, line in enumerate(code_lines):
            is_line_of_interest = i in lines_of_interest
            should_show_line = i in show_lines
            if should_show_line:
                line_prefix = "█" if is_line_of_interest else "│"
                formatted_lines.append(f"{line_prefix}{line}")
            else:
                if i == 0 or (i - 1) in show_lines:
                    formatted_lines.append("⋮...")
        return "\n".join(formatted_lines)

    def _create_metadata(self) -> dict[str, Any]:
        return {"processor_type": "code-outliner"}

    def _extract_all_definitions(
        self, sources: list[Source], tagger: ASTBasedTagger
    ) -> list[Definition]:
        all_definitions = []
        for source in sources:
            if self._should_process_source(source):
                definitions = tagger.extract_definitions(source)
                all_definitions.extend(definitions)
        return all_definitions

    def _generate_sample_definitions(
        self, all_definitions: list[Definition], max_samples: int = 2
    ) -> list[tuple[str, str]]:
        definitions_with_names = [d for d in all_definitions if d.name and d.name.text]
        if not definitions_with_names:
            return []
        sampled = random.sample(
            definitions_with_names, min(max_samples, len(definitions_with_names))
        )
        return [(d.rel_path, cast(Tag, d.name).text) for d in sampled]

    def _empty_result(self) -> Excerpts:
        return Excerpts([], {"sample_definitions": []})
