import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from llm_context.file_selector import FileSelector
from llm_context.profile import MEDIA_EXTENSIONS
from llm_context.utils import _format_size, format_age


@dataclass(frozen=True)
class FlatDiagram:
    root_dir: str
    full_files: Optional[set[str]] = None
    outline_files: Optional[set[str]] = None

    def _get_status(self, path: str) -> str:
        if self.full_files and path in self.full_files:
            return "✓"
        if self.outline_files and path in self.outline_files:
            return "○"
        return "✗"

    def _is_media(self, path: str) -> bool:
        return Path(path).suffix.lower() in MEDIA_EXTENSIONS

    def generate(self, abs_paths: list[str]) -> str:
        if not abs_paths:
            return "No files found"

        header = "Status: ✓=Full content, ○=Outline only, ✗=Excluded\n"
        header += "Format: status path bytes (size) age\n\n"

        entries = []
        for path in sorted(abs_paths):
            status = self._get_status(path)
            rel_path = f"/{Path(self.root_dir).name}/{Path(path).relative_to(self.root_dir)}"
            size = os.path.getsize(path)
            age = format_age(os.path.getmtime(path))

            entries.append(f"{status} {rel_path} {size} ({_format_size(size)}) {age}")

        return header + "\n".join(entries)


def get_flat_diagram(
    project_root: Path,
    full_files: list[str],
    outline_files: list[str],
    diagram_ignores: list[str] = [],
) -> str:
    abs_paths = FileSelector.create_universal(project_root).get_files()
    diagram_ignorer = FileSelector.create_ignorer(project_root, diagram_ignores)
    abs_filtered = diagram_ignorer.filter_files(abs_paths)
    diagram = FlatDiagram(str(project_root), set(full_files), set(outline_files))
    return diagram.generate(abs_filtered)
