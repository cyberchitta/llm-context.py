from dataclasses import dataclass
from typing import Any, Optional, Type

from llm_context.excerpters.base import Excerpter, Excerpts
from llm_context.excerpters.code_outliner import CodeOutliner
from llm_context.excerpters.parser import Source
from llm_context.excerpters.sfc import Sfc
from llm_context.rule import Rule  # Import for type


@dataclass(frozen=True)
class ExcerpterRegistry:
    excerpters: dict[str, Type[Excerpter]]

    @staticmethod
    def create() -> "ExcerpterRegistry":
        return ExcerpterRegistry(
            {
                "code-outliner": CodeOutliner,
                "sfc": Sfc,
            }
        )

    def get_excerpter(self, excerpter_name: str, config: dict[str, Any]) -> Optional[Excerpter]:
        excerpter_class = self.excerpters.get(excerpter_name)
        return excerpter_class(config) if excerpter_class else None  # type: ignore[call-arg]

    def excerpt(self, sources: list[Source], rule: Rule, tagger: Any) -> list[Excerpts]:
        if not rule.excerpt_modes:
            raise ValueError(
                f"Rule {rule.name} has no excerpt-modes configured. Add excerpt-modes or compose 'lc/exc-base'."
            )
        sources_by_mode: dict[str, list[Source]] = {}
        for source in sources:
            excerpt_mode = rule.get_excerpt_mode(source.rel_path)
            if excerpt_mode:
                if excerpt_mode not in sources_by_mode:
                    sources_by_mode[excerpt_mode] = []
                sources_by_mode[excerpt_mode].append(source)
        all_excerpts: list[Excerpts] = []
        for excerpt_mode, mode_sources in sources_by_mode.items():
            excerpt_config = rule.get_excerpt_config(excerpt_mode)
            excerpt_config["tagger"] = tagger
            excerpter = self.get_excerpter(excerpt_mode, excerpt_config)
            if excerpter:
                excerpts = excerpter.excerpt(mode_sources)
                all_excerpts.extend([excerpts])
        return all_excerpts

    def empty(self) -> list[Excerpts]:
        return [Excerpts([], {"sample_definitions": []})]
