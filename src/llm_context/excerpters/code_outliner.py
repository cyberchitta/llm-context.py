from dataclasses import dataclass
from typing import Any

from llm_context.excerpters.base import Excerpt, Excerpter, Excerpts, Excluded
from llm_context.excerpters.outliner import generate_outlines
from llm_context.excerpters.parser import Source


@dataclass(frozen=True)
class CodeOutliner(Excerpter):
    config: dict[str, Any]

    def excerpt(self, sources: list[Source]) -> Excerpts:
        if not sources:
            return Excerpts([], {"sample_definitions": []})
        outlines, sample_definitions = generate_outlines(self.config["tagger"], sources)
        results = []
        for outline in outlines:
            result = Excerpt(
                outline["rel_path"],
                outline["excerpts"],
                {
                    "processor_type": "code-outliner",
                },
            )
            results.append(result)
        return Excerpts(results, {"sample_definitions": sample_definitions})

    def excluded(self, sources: list[Source]) -> list[Excluded]:
        return []
