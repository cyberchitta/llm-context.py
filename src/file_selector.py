import os
from typing import List

from config_manager import ConfigManager
from composite_ignorer import CompositeIgnorer
from gitignore_parser import GitignoreParser

class FileSelector:
    @classmethod
    def create(cls) -> "FileSelector":
        config_manager = ConfigManager.create_default()
        gitignore_parser = GitignoreParser.create(
            config_manager.user["root_path"], config_manager.project["gitignores"]
        )
        composite_ignorer = gitignore_parser.create_composite_ignorer()
        return cls(config_manager, composite_ignorer)

    def __init__(self, config_manager: ConfigManager, composite_ignorer: CompositeIgnorer):
        self.config_manager = config_manager
        self.composite_ignorer = composite_ignorer

    def traverse(self, current_dir: str) -> List[str]:
        entries = os.listdir(current_dir)
        dirs = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and os.path.isdir(e_path)
            and not self.composite_ignorer.ignore(e_path, e, is_dir=True)
        ]
        files = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and not os.path.isdir(e_path)
            and not self.composite_ignorer.ignore(e_path, e, is_dir=False)
        ]
        subdir_files = [file for d in dirs for file in self.traverse(d)]
        return files + subdir_files

    def get_all(self) -> List[str]:
        return self.traverse(self.config_manager.user["root_path"])

    def update_selected(self) -> None:
        all_files = self.get_all()
        self.config_manager.update_files(all_files)


def main():
    select_files = FileSelector.create()
    select_files.update_selected()


if __name__ == "__main__":
    main()
