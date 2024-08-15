import os
from typing import List, Optional

from llm_code_context.config_manager import ConfigManager
from llm_code_context.git_ignorer import GitIgnorer
from llm_code_context.pathspec_ignorer import PathspecIgnorer


class FileSelector:
    @classmethod
    def create(cls, pathspecs: Optional[List[str]] = None) -> "FileSelector":
        config_manager = ConfigManager.create_default()
        if pathspecs is None:
            pathspecs = config_manager.project["gitignores"]
        git_ignorer = GitIgnorer.from_git_root(config_manager.project_path(), pathspecs)
        return cls(config_manager, git_ignorer)

    def __init__(self, config_manager: ConfigManager, ignorer: PathspecIgnorer):
        self.config_manager = config_manager
        self.ignorer = ignorer

    def traverse(self, current_dir: str) -> List[str]:
        entries = os.listdir(current_dir)
        root_path = self.config_manager.project_path()
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

    def get_all(self) -> List[str]:
        return self.traverse(self.config_manager.project_path())

    def update_selected(self) -> None:
        all_files = self.get_all()
        self.config_manager.select_files(all_files)


def main():
    select_files = FileSelector.create()
    select_files.update_selected()


if __name__ == "__main__":
    main()
