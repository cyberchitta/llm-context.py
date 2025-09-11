from dataclasses import dataclass

from llm_context.excerpt_processor import ExcerptedContent, ExcerptProcessor, ExcludedSections
from llm_context.highlighter.outliner import generate_outlines
from llm_context.highlighter.parser import ASTFactory, Source
from llm_context.highlighter.tagger import ASTBasedTagger


@dataclass(frozen=True)
class TreeSitterOutlineProcessor(ExcerptProcessor):
    def excerpt(self, source: Source) -> ExcerptedContent:
        tagger = ASTBasedTagger.create(source.rel_path, ASTFactory.create())
        outlines, sample_defs = generate_outlines(tagger, [source])
        content = "\n".join([o["content"] for o in outlines]) if outlines else ""
        return ExcerptedContent(content, len(source.code), len(content), "tree-sitter-outline")

    def get_excluded_sections(self, source: Source) -> ExcludedSections:
        return ExcludedSections({}, {})
