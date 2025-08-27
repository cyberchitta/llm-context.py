import os
from dataclasses import dataclass
from logging import ERROR, WARNING
from pathlib import Path
from typing import Optional

from pathspec import GitIgnoreSpec  # type: ignore

from llm_context.context_spec import ContextSpec
from llm_context.rule import IGNORE_NOTHING, INCLUDE_ALL
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, log, safe_read_file


@dataclass(frozen=True)
class PathspecIgnorer:
    pathspec: GitIgnoreSpec

    @staticmethod
    def create(ignore_patterns: list[str]) -> "PathspecIgnorer":
        pathspec = GitIgnoreSpec.from_lines(ignore_patterns)
        return PathspecIgnorer(pathspec)

    def ignore(self, path: str) -> bool:
        assert path not in ("/", ""), "Root directory cannot be an input for ignore method"
        return self.pathspec.match_file(path)


@dataclass(frozen=True)
class GitIgnorer:
    ignorer_data: list[tuple[str, PathspecIgnorer]]

    @staticmethod
    def from_git_root(root_dir: str, xtra_root_patterns: list[str] = []) -> "GitIgnorer":
        ignorer_data = []
        if xtra_root_patterns:
            ignorer_data.append(("/", PathspecIgnorer.create(xtra_root_patterns)))
        gitignores = GitIgnorer._collect_gitignores(root_dir)
        for relative_path, patterns in gitignores:
            ignorer_data.append((relative_path, PathspecIgnorer.create(patterns)))
        start_idx = 1 if xtra_root_patterns else 0
        if len(ignorer_data) > start_idx:
            prefix_data = ignorer_data[:start_idx]
            gitignore_data = ignorer_data[start_idx:]
            gitignore_data.sort(key=lambda x: (-x[0].count("/"), x[0]))
            ignorer_data = prefix_data + gitignore_data
        return GitIgnorer(ignorer_data)

    @staticmethod
    def _collect_gitignores(top: str) -> list[tuple[str, list[str]]]:
        gitignores = []
        for root, _, files in os.walk(top):
            if ".gitignore" in files:
                content = safe_read_file(os.path.join(root, ".gitignore"))
                if content:
                    patterns = content.splitlines()
                    relpath = os.path.relpath(root, top)
                    fixpath = "/" if relpath == "." else f"/{relpath}"
                    gitignores.append((fixpath, patterns))
        return gitignores

    def ignore(self, path: str) -> bool:
        assert path not in ("/", ""), "Root directory cannot be an input for ignore method"
        for prefix, ignorer in self.ignorer_data:
            if path.startswith(prefix):
                if prefix == "/":
                    test_path = path[1:]
                else:
                    test_path = path[len(prefix) :].lstrip("/")
                if test_path and ignorer.ignore(test_path):
                    return True
        return False


@dataclass(frozen=True)
class IncludeFilter:
    pathspec: GitIgnoreSpec

    @staticmethod
    def create(include_patterns: list[str]) -> "IncludeFilter":
        pathspec = GitIgnoreSpec.from_lines(include_patterns)
        return IncludeFilter(pathspec)

    def include(self, path: str) -> bool:
        assert path not in ("/", ""), "Root directory cannot be an input for include method"
        return self.pathspec.match_file(path)


@dataclass(frozen=True)
class FileSelector:
    root_path: str
    ignorer: GitIgnorer
    converter: PathConverter
    limit_filter: IncludeFilter
    also_include_filter: IncludeFilter
    since: Optional[float]

    @staticmethod
    def create_universal(root_path: Path) -> "FileSelector":
        return FileSelector.create_ignorer(root_path, IGNORE_NOTHING)

    @staticmethod
    def create_ignorer(root_path: Path, pathspecs: list[str]) -> "FileSelector":
        return FileSelector.create(root_path, pathspecs, INCLUDE_ALL, [])

    @staticmethod
    def create(
        root_path: Path,
        ignore_pathspecs: list[str],
        limit_to_pathspecs: list[str],
        also_include_pathspecs: list[str],
        since: Optional[float] = None,
    ) -> "FileSelector":
        ignorer = GitIgnorer.from_git_root(str(root_path), ignore_pathspecs)
        converter = PathConverter.create(root_path)
        limit_filter = IncludeFilter.create(limit_to_pathspecs)
        also_include_filter = IncludeFilter.create(also_include_pathspecs)
        return FileSelector(
            str(root_path), ignorer, converter, limit_filter, also_include_filter, since
        )

    def filter_files(self, files: list[str]) -> list[str]:
        return [f for f in files if f in set(self.get_files())]

    def get_files(self) -> list[str]:
        files = list(set(self.traverse(self.root_path) + self.also_traverse(self.root_path)))
        return [f for f in files if Path(f).stat().st_mtime > self.since] if self.since else files

    def get_relative_files(self) -> list[str]:
        return sorted(self.converter.to_relative(self.get_files()))

    def traverse(self, current_dir: str) -> list[str]:
        entries = os.listdir(current_dir)
        relative_current_dir = os.path.relpath(current_dir, self.root_path)
        dirs = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and os.path.isdir(e_path)
            and (not self.ignorer.ignore(self._relative_path(relative_current_dir, e)))
        ]
        files = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and not os.path.isdir(e_path)
            and self._should_include_file(self._relative_path(relative_current_dir, e))
        ]
        subdir_files = [file for d in dirs for file in self.traverse(d)]
        return files + subdir_files

    def _should_include_file(self, path: str) -> bool:
        assert path not in ("/", ""), "Root directory cannot be an input for filtering"
        if self.ignorer.ignore(path):
            return False
        return self.limit_filter.include(path)

    def also_traverse(self, current_dir: str) -> list[str]:
        if not self.also_include_filter.pathspec.patterns:
            return []
        entries = os.listdir(current_dir)
        relative_current_dir = os.path.relpath(current_dir, self.root_path)
        dirs = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e)) and os.path.isdir(e_path)
        ]
        files = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and not os.path.isdir(e_path)
            and self.also_include_filter.include(self._relative_path(relative_current_dir, e))
        ]
        subdir_files = [file for d in dirs for file in self.also_traverse(d)]
        return files + subdir_files

    def _relative_path(self, dir: str, filename: str) -> str:
        return f"/{os.path.normpath(os.path.join(dir, filename))}"


@dataclass(frozen=True)
class ContextSelector:
    full_selector: FileSelector
    outline_selector: FileSelector

    @staticmethod
    def create(spec: ContextSpec, since: Optional[float] = None) -> "ContextSelector":
        root_path = spec.project_root_path
        rule = spec.rule
        full_ignore_pathspecs = rule.get_ignore_patterns("full")
        outline_ignore_pathspecs = rule.get_ignore_patterns("outline")
        full_limit_to_pathspecs = rule.get_limit_to_patterns("full")
        outline_limit_to_pathspecs = rule.get_limit_to_patterns("outline")
        full_also_include_pathspecs = rule.get_also_include_patterns("full")
        outline_also_include_pathspecs = rule.get_also_include_patterns("outline")
        full_selector = FileSelector.create(
            root_path,
            full_ignore_pathspecs,
            full_limit_to_pathspecs,
            full_also_include_pathspecs,
            since,
        )
        outline_selector = FileSelector.create(
            root_path,
            outline_ignore_pathspecs,
            outline_limit_to_pathspecs,
            outline_also_include_pathspecs,
            since,
        )
        return ContextSelector(full_selector, outline_selector)

    def select_full_files(self, file_selection: FileSelection) -> "FileSelection":
        full_files = self.full_selector.get_relative_files()
        outline_files = file_selection.outline_files
        updated_outline_files = [f for f in outline_files if f not in set(full_files)]
        if len(outline_files) != len(updated_outline_files):
            log(
                WARNING,
                "Some files previously in outline selection have been moved to full selection.",
            )
        return FileSelection._create(
            file_selection.rule_name, full_files, updated_outline_files, file_selection.timestamp
        )

    def select_outline_files(self, file_selection: FileSelection) -> "FileSelection":
        full_files = file_selection.full_files
        if not full_files:
            log(
                WARNING,
                "No full files have been selected. Consider running full file selection first.",
            )
        all_outline_files = self.outline_selector.get_relative_files()
        outline_files = [f for f in all_outline_files if f not in set(full_files)]
        return FileSelection._create(
            file_selection.rule_name, full_files, outline_files, file_selection.timestamp
        )

    def select_outline_only(self, file_selection: FileSelection) -> "FileSelection":
        all_outline_files = self.outline_selector.get_relative_files()
        return FileSelection._create(
            file_selection.rule_name, [], all_outline_files, file_selection.timestamp
        )
