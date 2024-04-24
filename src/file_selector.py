import os
from config_manager import ConfigManager
from gitignore_parser import GitIgnoreParser

class FileSelector:
    @staticmethod
    def create():
        config_manager = ConfigManager.create_default()
        gitignore_parser = GitIgnoreParser.create(config_manager.user['root_path'])
        return FileSelector(config_manager, gitignore_parser)

    def __init__(self, config_manager, gitignore_parser):
        self.config_manager = config_manager
        self.gitignore_parser = gitignore_parser

    def get_all(self):
        root_directory = self.config_manager.user['root_path']
        ignore_dirs, self.ignore_files = self.gitignore_parser.parse()
        all_files = []
        for dirpath, dirnames, filenames in os.walk(root_directory):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            for filename in filenames:
                if filename not in self.ignore_files:
                    file_path = os.path.join(dirpath, filename)
                    all_files.append(file_path)
        return all_files

    def update_selected(self):
        all_files = self.get_all()
        self.config_manager.update_files(all_files)

def main():
    select_files = FileSelector.create()
    select_files.update_selected()

if __name__ == '__main__':
    main()