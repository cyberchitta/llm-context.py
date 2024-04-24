import os

from config_manager import ConfigManager
from gitignore_parser import GitignoreParser


class FileSelector:
    @staticmethod
    def create():
        config_manager = ConfigManager.create_default()
        gitignore_parser = GitignoreParser.create(
            config_manager.user["root_path"], list((".git", "*.lock"))
        )
        file_ignorer = gitignore_parser.create_file_ignorer()
        return FileSelector(config_manager, file_ignorer)

    def __init__(self, config_manager, file_ignorer):
        self.config_manager = config_manager
        self.file_ignorer = file_ignorer

    def traverse(self, current_dir):
        entries = os.listdir(current_dir)
        dirs = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and os.path.isdir(e_path)
            and not self.file_ignorer.ignore(e, is_dir=True)
        ]
        files = [
            e_path
            for e in entries
            if (e_path := os.path.join(current_dir, e))
            and not os.path.isdir(e_path)
            and not self.file_ignorer.ignore(e, is_dir=False)
        ]
        subdir_files = [file for d in dirs for file in self.traverse(d)]
        return files + subdir_files

    def get_all(self):
        return self.traverse(self.config_manager.user["root_path"])

    def update_selected(self):
        all_files = self.get_all()
        self.config_manager.update_files(all_files)


def main():
    select_files = FileSelector.create()
    select_files.update_selected()


if __name__ == "__main__":
    main()
