from dataclasses import dataclass

from llm_context.context_generator import ContextCollector, Template
from llm_context.context_spec import ContextSpec
from llm_context.file_selector import ContextSelector
from llm_context.state import FileSelection
from llm_context.utils import ProjectLayout, _format_size


@dataclass(frozen=True)
class FileStats:
    rel_path: str
    original_bytes: int
    excerpted_bytes: int | None = None  # None for full files


@dataclass(frozen=True)
class ContextPreview:
    rule_name: str
    compose_filters: list[str]
    compose_excerpters: list[str]
    full_files: list[FileStats]
    excerpted_files: list[FileStats]
    project_layout: ProjectLayout
    template_name: str

    @staticmethod
    def create(config: ContextSpec, tagger) -> "ContextPreview":
        rule = config.rule
        selector = ContextSelector.create(config)
        collector = ContextCollector.create(config.project_root_path)
        empty_selection = FileSelection.create(rule.name, [], [])
        file_selection = selector.select_full_files(empty_selection)
        file_selection = selector.select_excerpted_files(file_selection)
        full_stats = [
            FileStats(path, size) for path, size in collector.file_stats(file_selection.full_files)
        ]
        excerpted_stats = [
            FileStats(path, orig, excerpt)
            for path, orig, excerpt in collector.excerpt_stats(
                tagger, file_selection.excerpted_files, rule
            )
        ]
        return ContextPreview(
            rule_name=rule.name,
            compose_filters=rule.compose.filters,
            compose_excerpters=rule.compose.excerpters,
            full_files=full_stats,
            excerpted_files=excerpted_stats,
            project_layout=config.project_layout,
            template_name=config.templates["preview"],
        )

    @property
    def full_total_bytes(self) -> int:
        return sum(f.original_bytes for f in self.full_files)

    @property
    def excerpted_total_bytes(self) -> int:
        return sum(f.excerpted_bytes or 0 for f in self.excerpted_files)

    @property
    def excerpted_original_bytes(self) -> int:
        return sum(f.original_bytes for f in self.excerpted_files)

    @property
    def total_bytes(self) -> int:
        return self.full_total_bytes + self.excerpted_total_bytes

    @property
    def estimated_tokens(self) -> int:
        return self.total_bytes // 4

    def format(self, max_files: int = 15) -> str:
        sorted_full = sorted(self.full_files, key=lambda x: -x.original_bytes)
        sorted_excerpted = sorted(self.excerpted_files, key=lambda x: -(x.excerpted_bytes or 0))
        full_file_data = [
            {
                "rel_path": f.rel_path,
                "original_size": _format_size(f.original_bytes),
            }
            for f in sorted_full
        ]
        excerpted_file_data = [
            {
                "rel_path": f.rel_path,
                "original_size": _format_size(f.original_bytes),
                "excerpted_size": _format_size(f.excerpted_bytes or 0),
            }
            for f in sorted_excerpted
        ]
        context = {
            "rule_name": self.rule_name,
            "compose_filters": self.compose_filters,
            "compose_excerpters": self.compose_excerpters,
            "full_files": full_file_data,
            "excerpted_files": excerpted_file_data,
            "full_total_size": _format_size(self.full_total_bytes),
            "excerpted_total_size": _format_size(self.excerpted_total_bytes),
            "excerpted_original_size": _format_size(self.excerpted_original_bytes),
            "total_files": len(self.full_files) + len(self.excerpted_files),
            "total_size": _format_size(self.total_bytes),
            "estimated_tokens": self.estimated_tokens // 1000,
            "max_files": max_files,
        }
        template = Template.create(self.template_name, context, self.project_layout.templates_path)
        return template.render()
