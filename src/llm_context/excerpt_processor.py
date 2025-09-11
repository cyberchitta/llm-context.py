from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from llm_context.highlighter.parser import Source
from llm_context.rule import Rule  # Import for type


@dataclass(frozen=True)
class ExcerptedContent:
    content: str
    original_size: int
    excerpted_size: int
    processor_type: str

    @property
    def reduction_ratio(self) -> float:
        if self.original_size == 0:
            return 0.0
        return 1.0 - (self.excerpted_size / self.original_size)


@dataclass(frozen=True)
class ExcludedSections:
    sections: Dict[str, str]  # section_name -> content
    metadata: Dict[str, Any]


class ExcerptProcessor(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def excerpt(self, source: Source) -> ExcerptedContent:
        """Extract important sections from source."""
        pass

    @abstractmethod
    def get_excluded_sections(self, source: Source) -> ExcludedSections:
        """Return sections that were excluded from excerpt."""
        pass


@dataclass(frozen=True)
class ExcerptProcessorRegistry:
    processors: Dict[str, Type[ExcerptProcessor]]

    @staticmethod
    def create() -> "ExcerptProcessorRegistry":
        from llm_context.excerpt_processors.tree_sitter_outline import TreeSitterOutlineProcessor

        return ExcerptProcessorRegistry(
            {
                "tree-sitter-outline": TreeSitterOutlineProcessor,
            }
        )

    def get_processor(
        self, processor_name: str, config: Dict[str, Any]
    ) -> Optional[ExcerptProcessor]:
        processor_class = self.processors.get(processor_name)
        return processor_class(config) if processor_class else None

    def excerpt(
        self, sources: List[Source], rule: Rule, tagger: Any
    ) -> tuple[list[dict[str, str]], list[tuple[str, str]]]:
        """excerpts = []
        for source in sources:
            mode = rule.get_excerpt_mode(source.rel_path)
            if mode:
                processor = self.get_processor(mode, {})
                if processor:
                    exc_content = processor.excerpt(source)
                    excerpts.append(
                        {
                            "path": source.rel_path,
                            "content": exc_content.content,
                            "metadata": {
                                "original_size": exc_content.original_size,
                                "excerpted_size": exc_content.excerpted_size,
                                "reduction": exc_content.reduction_ratio,
                            },
                        }
                    )
        return excerpts
        """
        from llm_context.highlighter.outliner import generate_outlines

        return generate_outlines(tagger, sources)
