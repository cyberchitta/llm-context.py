"""Which files does a selection reference, but not include?

Built from tag matches the parser already produces. `to_definition` keeps only
`definition.*` captures; the `reference.*` captures alongside them are what this
module uses, so the graph costs one extra pass over files, not new machinery.

Matching is by symbol name, which is an approximation: a name defined in many
places cannot be attributed to any one of them, so symbols defined in more than
MAX_DEFINING_FILES files are dropped rather than guessed at. The result is a
ranked hint for a human or agent reading `lc-preview`, never an automatic
expansion of the selection.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from llm_context.excerpters.language_mapping import to_language
from llm_context.excerpters.parser import Source
from llm_context.utils import PathConverter, safe_read_file

MAX_DEFINING_FILES = 3


@dataclass(frozen=True)
class DependencyGap:
    rel_path: str
    reference_count: int
    symbols: list[str]


@dataclass(frozen=True)
class SymbolIndex:
    definers: dict[str, set[str]]
    referenced_by: dict[str, set[str]]
    parsed: int = 0
    failed: int = 0

    @property
    def unusable(self) -> bool:
        """Nothing parsed at all - report that, rather than an empty result.

        An empty gap list means "your selection is closed". A parser that failed
        on every file produces the same empty list and means nothing of the sort.
        """
        return self.parsed == 0 and self.failed > 0

    @staticmethod
    def create(tagger, root_path: Path, rel_paths: list[str]) -> "SymbolIndex":
        converter = PathConverter.create(root_path)
        definers: dict[str, set[str]] = defaultdict(set)
        referenced_by: dict[str, set[str]] = defaultdict(set)
        parsed = failed = 0
        for rel_path, abs_path in zip(rel_paths, converter.to_absolute(rel_paths)):
            if not to_language(rel_path):
                continue
            content = safe_read_file(abs_path)
            if content is None:
                continue
            source = Source(rel_path, content)
            try:
                definitions = tagger.extract_definitions(source)
                references = tagger.extract_references(source)
            except Exception:
                failed += 1
                continue
            parsed += 1
            for definition in definitions:
                if definition.name:
                    definers[definition.name.text].add(rel_path)
            for reference in references:
                referenced_by[rel_path].add(reference.name)
        return SymbolIndex(dict(definers), dict(referenced_by), parsed, failed)

    def gaps(
        self, selected: list[str], max_defining_files: int = MAX_DEFINING_FILES
    ) -> list[DependencyGap]:
        chosen = set(selected)
        counts: Counter = Counter()
        symbols: dict[str, set[str]] = defaultdict(set)
        for rel_path in chosen:
            for symbol in self.referenced_by.get(rel_path, set()):
                owners = self.definers.get(symbol, set())
                if not owners or len(owners) > max_defining_files:
                    continue
                for owner in owners - chosen:
                    counts[owner] += 1
                    symbols[owner].add(symbol)
        return [
            DependencyGap(rel_path, count, sorted(symbols[rel_path]))
            for rel_path, count in counts.most_common()
        ]
