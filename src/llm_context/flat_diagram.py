import os
from dataclasses import dataclass
from pathlib import Path

from llm_context.file_selector import FileSelector
from llm_context.utils import _format_size, format_age

STATUSES = ["✅", "✓", "○", "✗"]

STATUS_DESCRIPTIONS = {
    "✅": "Key files (explicitly selected full content)",
    "✓": "Full content",
    "○": "Outline only",
    "✗": "Excluded",
}


@dataclass(frozen=True)
class FlatDiagram:
    root_dir: str
    full_files: set[str]
    outline_files: set[str]
    rule_files: set[str]

    def _get_status(self, path: str) -> str:
        if self.rule_files and path in self.rule_files:
            return "✅"
        if self.full_files and path in self.full_files:
            return "✓"
        if self.outline_files and path in self.outline_files:
            return "○"
        return "✗"

    def _legend(self, status: str) -> str:
        return f"{status}={STATUS_DESCRIPTIONS[status]}"

    @property
    def _file_info_header(self):
        return "status path bytes (size) age"

    def _file_info(self, abs_path: str) -> tuple[str, str]:
        return (
            self._get_status(abs_path),
            f"/{Path(self.root_dir).name}/{Path(abs_path).relative_to(self.root_dir)} "
            f"{os.path.getsize(abs_path)}"
            f"({_format_size(os.path.getsize(abs_path))})"
            f"{format_age(os.path.getmtime(abs_path))}",
        )

    def generate(self, abs_paths: list[str]) -> str:
        if not abs_paths:
            return "No files found"
        entries = [self._file_info(path) for path in sorted(abs_paths)]
        used = set(status for status, _ in entries)
        legends = [self._legend(status) for status in STATUSES if status in used]
        header = f"Status: {', '.join(legends)}\n"
        header += f"Format: {self._file_info_header}\n\n"
        rows = [f"{status} {entry}" for status, entry in entries]
        return header + "\n".join(rows)


def get_flat_diagram(
    project_root: Path,
    full_files: list[str],
    outline_files: list[str],
    rule_files: list[str],
    diagram_ignores: list[str] = [],
) -> str:
    diagram_ignorer = FileSelector.create_ignorer(project_root, diagram_ignores)
    abs_paths = diagram_ignorer.get_files()
    diagram = FlatDiagram(str(project_root), set(full_files), set(outline_files), set(rule_files))
    return diagram.generate(abs_paths)
