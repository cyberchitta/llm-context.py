import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

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
class OverviewHelper:
    root_dir: str
    full_files: set[str]
    outline_files: set[str]
    rule_files: set[str]

    def get_status(self, path: str) -> str:
        if self.rule_files and path in self.rule_files:
            return "✅"
        if self.full_files and path in self.full_files:
            return "✓"
        if self.outline_files and path in self.outline_files:
            return "○"
        return "✗"

    def get_legend(self, status: str) -> str:
        return f"{status}={STATUS_DESCRIPTIONS[status]}"

    def get_used_statuses(self, abs_paths: list[str]) -> list[str]:
        used = {self.get_status(path) for path in abs_paths}
        return [status for status in STATUSES if status in used]

    def format_legend_header(self, abs_paths: list[str]) -> str:
        used_statuses = self.get_used_statuses(abs_paths)
        legends = [self.get_legend(status) for status in used_statuses]
        return f"Status: {', '.join(legends)}\nFormat: status path bytes (size) age\n\n"

    def get_file_info(self, abs_path: str) -> tuple[str, str]:
        return (
            self.get_status(abs_path),
            f"/{Path(self.root_dir).name}/{Path(abs_path).relative_to(self.root_dir)} "
            f"{os.path.getsize(abs_path)}"
            f"({_format_size(os.path.getsize(abs_path))})"
            f"{format_age(os.path.getmtime(abs_path))}",
        )


@dataclass(frozen=True)
class FullOverview:
    helper: OverviewHelper

    @staticmethod
    def create(
        root_dir: str, full_files: set[str], outline_files: set[str], rule_files: set[str]
    ) -> "FullOverview":
        helper = OverviewHelper(root_dir, full_files, outline_files, rule_files)
        return FullOverview(helper)

    def generate(self, abs_paths: list[str]) -> str:
        if not abs_paths:
            return "No files found"
        entries = [self.helper.get_file_info(path) for path in sorted(abs_paths)]
        header = self.helper.format_legend_header(abs_paths)
        rows = [f"{status} {entry}" for status, entry in entries]
        return header + "\n".join(rows)


@dataclass(frozen=True)
class FocusedOverview:
    helper: OverviewHelper

    @staticmethod
    def create(
        root_dir: str, full_files: set[str], outline_files: set[str], rule_files: set[str]
    ) -> "FocusedOverview":
        helper = OverviewHelper(root_dir, full_files, outline_files, rule_files)
        return FocusedOverview(helper)

    def _group_files_by_immediate_parent(self, abs_paths: list[str]) -> Dict[str, list[str]]:
        folders: Dict[str, list[str]] = {}

        for abs_path in abs_paths:
            parent_path = str(Path(abs_path).parent)
            if parent_path not in folders:
                folders[parent_path] = []
            folders[parent_path].append(abs_path)

        return folders

    def _folder_has_included_files(self, files_in_folder: list[str]) -> bool:
        return any(self.helper.get_status(f) in ["✅", "✓", "○"] for f in files_in_folder)

    def _format_folder_with_file_details(self, folder_path: str, files_in_folder: list[str]) -> str:
        root_name = Path(self.helper.root_dir).name
        folder_relative = Path(folder_path).relative_to(self.helper.root_dir)
        folder_display = (
            f"/{root_name}/{folder_relative}/" if str(folder_relative) != "." else f"/{root_name}/"
        )
        lines = [f"{folder_display} ({len(files_in_folder)} files)"]
        for file_path in sorted(files_in_folder):
            status = self.helper.get_status(file_path)
            filename = Path(file_path).name
            file_size = os.path.getsize(file_path)
            file_age = format_age(os.path.getmtime(file_path))
            indented_line = f"  {status} {filename} {_format_size(file_size)} {file_age}"
            lines.append(indented_line)
        return "\n".join(lines)

    def _format_folder_summary(self, folder_path: str, files_in_folder: list[str]) -> str:
        root_name = Path(self.helper.root_dir).name
        folder_relative = Path(folder_path).relative_to(self.helper.root_dir)
        folder_display = (
            f"/{root_name}/{folder_relative}/" if str(folder_relative) != "." else f"/{root_name}/"
        )
        total_size = sum(os.path.getsize(f) for f in files_in_folder)
        return f"{folder_display} ({len(files_in_folder)} files, {_format_size(total_size)})"

    def generate(self, abs_paths: list[str]) -> str:
        if not abs_paths:
            return "No files found"
        folders = self._group_files_by_immediate_parent(abs_paths)
        header = self.helper.format_legend_header(abs_paths)
        sections = []
        for folder_path in sorted(folders.keys()):
            files_in_folder = folders[folder_path]
            if self._folder_has_included_files(files_in_folder):
                sections.append(self._format_folder_with_file_details(folder_path, files_in_folder))
            else:
                sections.append(self._format_folder_summary(folder_path, files_in_folder))
        return header + "\n".join(sections)


def get_full_overview(
    project_root: Path,
    full_files: list[str],
    outline_files: list[str],
    rule_files: list[str],
    overview_ignores: list[str] = [],
) -> str:
    overview_ignorer = FileSelector.create_ignorer(project_root, overview_ignores)
    abs_paths = overview_ignorer.get_files()
    overview = FullOverview.create(
        str(project_root), set(full_files), set(outline_files), set(rule_files)
    )
    return overview.generate(abs_paths)


def get_focused_overview(
    project_root: Path,
    full_files: list[str],
    outline_files: list[str],
    rule_files: list[str],
    overview_ignores: list[str] = [],
) -> str:
    overview_ignorer = FileSelector.create_ignorer(project_root, overview_ignores)
    abs_paths = overview_ignorer.get_files()
    overview = FocusedOverview.create(
        str(project_root), set(full_files), set(outline_files), set(rule_files)
    )
    return overview.generate(abs_paths)
