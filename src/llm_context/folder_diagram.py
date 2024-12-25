import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, cast

from llm_context.file_selector import FileSelector
from llm_context.profile import IGNORE_NOTHING, INCLUDE_ALL, MEDIA_EXTENSIONS


@dataclass(frozen=True)
class FolderStructureDiagram:
    root_dir: str
    full_files: Optional[set[str]] = None
    outline_files: Optional[set[str]] = None
    no_media: bool = False

    @property
    def is_enhanced(self) -> bool:
        return self.full_files is not None and self.outline_files is not None

    @staticmethod
    def create_simple(root_dir: str) -> "FolderStructureDiagram":
        return FolderStructureDiagram(root_dir)

    @staticmethod
    def create_enhanced(
        root_dir: str, full_files: set[str], outline_files: set[str], no_media
    ) -> "FolderStructureDiagram":
        return FolderStructureDiagram(root_dir, full_files, outline_files, no_media)

    def generate_tree(self, in_abs_paths: list[str]) -> str:
        abs_paths = (
            [path for path in in_abs_paths if not self.is_excluded_file(path)]
            if self.no_media
            else in_abs_paths
        )
        sorted_paths = sorted(self._make_relative(path) for path in abs_paths)
        tree_dict = self._build_tree_structure(sorted_paths)
        diagram = self._format_tree({os.path.basename(self.root_dir): tree_dict})
        with_key = (
            "Key: ✓ Full content, ○ Outline only, ✗ Excluded\n\n" + diagram
            if self.is_enhanced
            else diagram
        )
        return (
            with_key + "\n\n*Non-text files have been excluded from this diagram.*"
            if self.no_media
            else with_key
        )

    def is_excluded_file(self, path: str) -> bool:
        return os.path.splitext(path)[1].lower() in MEDIA_EXTENSIONS

    def _make_relative(self, path: str) -> str:
        return os.path.relpath(path, self.root_dir)

    def _build_tree_structure(self, paths: list[str]) -> dict:
        root: dict = {}
        for path in paths:
            current = root
            for part in path.split(os.sep):
                if part not in current:
                    current[part] = {"__status__": self._get_file_status(path)}
                current = current[part]
        return root

    def _get_file_status(self, path: str) -> str:
        if not self.is_enhanced:
            return ""
        full_path = os.path.join(self.root_dir, path)
        if full_path in cast(set[str], self.full_files):
            return "✓"
        elif full_path in cast(set[str], self.outline_files):
            return "○"
        else:
            return "✗"

    def _format_tree(self, tree: dict, prefix: str = "") -> str:
        lines = []
        items = list(tree.items())
        for i, (name, subtree) in enumerate(items):
            is_last = i == len(items) - 1
            status = subtree.pop("__status__", "")
            lines.append(
                f"{prefix}{'└── ' if is_last else '├── '}{name}{' ' + status if status else ''}"
            )
            if subtree:
                extension = "    " if is_last else "│   "
                lines.append(self._format_tree(subtree, prefix + extension))
        return "\n".join(lines)


def get_annotated_fsd(
    project_root: Path, full_files: list[str], outline_files: list[str], no_media: bool
) -> str:
    abs_paths = FileSelector.create(project_root, IGNORE_NOTHING, INCLUDE_ALL).get_files()
    diagram = FolderStructureDiagram.create_enhanced(
        str(project_root), set(full_files), set(outline_files), no_media
    )
    return diagram.generate_tree(abs_paths)


def get_fsd() -> str:
    project_root = Path.cwd()
    abs_paths = FileSelector.create(project_root, IGNORE_NOTHING, INCLUDE_ALL).get_files()
    diagram = FolderStructureDiagram.create_simple(str(project_root))
    return diagram.generate_tree(abs_paths)
