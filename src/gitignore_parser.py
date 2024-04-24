import os

class GitIgnoreParser:
    @staticmethod
    def create(root_directory):
        gitignore_file = os.path.join(root_directory, '.gitignore')
        additional_ignore_dirs = list(('.git', '.cache', '.venv'))
        additional_ignore_files = list(('.DS_Store', 'Thumbs.db'))
        return GitIgnoreParser(gitignore_file, additional_ignore_dirs, additional_ignore_files)

    def __init__(self, gitignore_file, additional_ignore_dirs, additional_ignore_files):
        self.gitignore_file = gitignore_file
        self.additional_ignore_dirs = additional_ignore_dirs
        self.additional_ignore_files = additional_ignore_files

    def parse(self):
        if not os.path.isfile(self.gitignore_file):
            return self.additional_ignore_dirs, self.additional_ignore_files

        with open(self.gitignore_file, 'r') as file:
            lines = file.readlines()

        ignore_dirs = [line.strip() for line in lines if line.strip().endswith('/')]
        ignore_files = [line.strip() for line in lines if not line.strip().endswith('/')]

        ignore_dirs = ignore_dirs + self.additional_ignore_dirs
        ignore_files = ignore_files + self.additional_ignore_files

        return ignore_dirs, ignore_files