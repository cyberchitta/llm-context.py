import os
import warnings
from dataclasses import dataclass
from pathlib import Path

from pathspec import GitIgnoreSpec

from llm_context.exceptions import LLMContextError
from llm_context.project_settings import ProjectSettings
from llm_context.utils import PathConverter, safe_read_file


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
        ignorer_data = [("/", PathspecIgnorer.create(xtra_root_patterns))]
        gitignores = GitIgnorer._collect_gitignores(root_dir)
        for relative_path, patterns in gitignores:
            ignorer_data.append((relative_path, PathspecIgnorer.create(patterns)))
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
                if ignorer.ignore(path):
                    return True
        return False


@dataclass(frozen=True)
class FileSelector:
    root_path: str
    ignorer: GitIgnorer
    converter: PathConverter

    @staticmethod
    def create(root_path: Path, pathspecs: list[str]) -> "FileSelector":
        ignorer = GitIgnorer.from_git_root(str(root_path), pathspecs)
        converter = PathConverter.create(root_path)
        return FileSelector(str(root_path), ignorer, converter)

    def get_files(self) -> list[str]:
        return self.traverse(self.root_path)

    def get_relative_files(self) -> list[str]:
        return self.converter.to_relative(self.get_files())

    def traverse(self, current_dir: str) -> list[str]:
        entries = os.listdir(current_dir)
        relative_current_dir = os.path.relpath(current_dir, self.root_path)
        dirs = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and os.path.isdir(e_path)
            and not self.ignorer.ignore(f"/{os.path.join(relative_current_dir, e)}/")
        ]
        files = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and not os.path.isdir(e_path)
            and not self.ignorer.ignore(f"/{os.path.join(relative_current_dir, e)}")
        ]
        subdir_files = [file for d in dirs for file in self.traverse(d)]
        return files + subdir_files


@dataclass(frozen=True)
class ContextSelector:
    settings: ProjectSettings
    full_selector: FileSelector
    outline_selector: FileSelector

    @staticmethod
    def create() -> "ContextSelector":
        settings = ProjectSettings.create()
        root_path = settings.project_root_path
        context_config = settings.context_config
        full_pathspecs = context_config.get_ignore_patterns("full")
        outline_pathspecs = context_config.get_ignore_patterns("outline")
        full_selector = FileSelector.create(root_path, full_pathspecs)
        outline_selector = FileSelector.create(root_path, outline_pathspecs)
        return ContextSelector(settings, full_selector, outline_selector)

    def select_full_files(self) -> list[str]:
        full_files = self.full_selector.get_relative_files()
        stored_context = self.settings.context_storage.get_stored_context()
        outline_files = stored_context.get("outline", [])
        updated_outline_files = [f for f in outline_files if f not in set(full_files)]
        if len(outline_files) != len(updated_outline_files):
            warnings.warn(
                "Some files previously in outline selection have been moved to full selection."
            )
        self.update_selected(full_files, updated_outline_files)
        return full_files

    def select_outline_files(self) -> list[str]:
        stored_context = self.settings.context_storage.get_stored_context()
        full_files = stored_context.get("full", [])
        if not full_files:
            warnings.warn(
                "No full files have been selected. Consider running full file selection first."
            )
        all_outline_files = self.outline_selector.get_relative_files()
        outline_files = [f for f in all_outline_files if f not in set(full_files)]
        self.update_selected(full_files, outline_files)
        return outline_files

    def update_selected(self, full_files: list[str], outline_files: list[str]):
        self.settings.context_storage.store_context({"full": full_files, "outline": outline_files})


@LLMContextError.handle
def select_full_files():
    full_files = ContextSelector.create().select_full_files()
    print(f"Selected {len(full_files)} full files.")


@LLMContextError.handle
def select_outline_files():
    outline_files = ContextSelector.create().select_outline_files()
    print(f"Selected {len(outline_files)} outline files.")


def main():
    selector = ContextSelector.create()
    full_files = selector.select_full_files()
    outline_files = selector.select_outline_files()
    selector.update_selected(full_files, outline_files)


if __name__ == "__main__":
    main()
