import os
from dataclasses import dataclass

from pathspec import GitIgnoreSpec

from llm_context.project_settings import ProjectSettings


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
    def _collect_gitignores(top) -> list[tuple[str, list[str]]]:
        gitignores = []
        for root, _, files in os.walk(top):
            if ".gitignore" in files:
                with open(os.path.join(root, ".gitignore"), "r") as file:
                    patterns = file.read().splitlines()
                relpath = os.path.relpath(root, top)
                fixpath = "/" if relpath == "." else f"/{os.path.relpath(root, top)}"
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

    @staticmethod
    def create(root_path: str, pathspecs: list[str]) -> "FileSelector":
        ignorer = GitIgnorer.from_git_root(root_path, pathspecs)
        return FileSelector(root_path, ignorer)

    def get_files(self) -> list[str]:
        return self.traverse(self.root_path)

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

    def get_all(self) -> list[str]:
        return self.traverse(self.root_path)


@dataclass(frozen=True)
class ContextSelector:
    project_settings: ProjectSettings
    full_selector: FileSelector
    outline_selector: FileSelector

    @staticmethod
    def create() -> "ContextSelector":
        project_settings = ProjectSettings.create()
        root_path = project_settings.project_root_path
        context_config = project_settings.context_config
        full_pathspecs = context_config.get_ignore_patterns("full")
        outline_pathspecs = context_config.get_ignore_patterns("outline")
        full_selector = FileSelector.create(root_path, full_pathspecs)
        outline_selector = FileSelector.create(root_path, outline_pathspecs)
        return ContextSelector(project_settings, full_selector, outline_selector)

    def select_files(self) -> tuple[list[str], list[str]]:
        full_content_files = self.full_selector.get_files()
        all_outline_files = self.outline_selector.get_files()
        outline_files = [f for f in all_outline_files if f not in set(full_content_files)]
        return full_content_files, outline_files

    def update_selected(self):
        full_content_files, outline_files = self.select_files()
        self.project_settings.context_storage.store_context(
            {"full": full_content_files, "outline": outline_files}
        )


def main():
    select_files = ContextSelector.create()
    select_files.select_files()
    select_files.update_selected()


if __name__ == "__main__":
    main()
