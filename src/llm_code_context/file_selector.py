import os
from dataclasses import dataclass

from pathspec import GitIgnoreSpec

from llm_code_context.config_manager import ConfigManager


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
    config_manager: ConfigManager
    ignorer: GitIgnorer

    @staticmethod
    def create(pathspecs: list[str] | None = None) -> "FileSelector":
        config_manager = ConfigManager.create_default()
        if pathspecs is None:
            pathspecs = config_manager.project["gitignores"]
        git_ignorer = GitIgnorer.from_git_root(config_manager.project_root_path(), pathspecs)
        return FileSelector(config_manager, git_ignorer)

    def traverse(self, current_dir: str) -> list[str]:
        entries = os.listdir(current_dir)
        root_path = self.config_manager.project_root()
        relative_current_dir = os.path.relpath(current_dir, root_path)
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
        return self.traverse(self.config_manager.project_root_path())

    def update_selected(self) -> None:
        all_files = self.get_all()
        self.config_manager.select_files(all_files)


def main():
    select_files = FileSelector.create()
    select_files.update_selected()


if __name__ == "__main__":
    main()
