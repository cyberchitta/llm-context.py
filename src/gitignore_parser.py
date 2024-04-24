import os

from file_ignorer import FileIgnorer


class GitignoreParser:
    @staticmethod
    def create_default(root_directory):
        additional_ignore_patterns = list((".git"))
        return GitignoreParser.create(root_directory, additional_ignore_patterns)

    @staticmethod
    def create(root_directory, additional_ignore_patterns):
        gitignore_file = os.path.join(root_directory, ".gitignore")
        return GitignoreParser(gitignore_file, additional_ignore_patterns)

    def __init__(self, gitignore_file, additional_ignore_patterns):
        self.gitignore_file = gitignore_file
        self.additional_ignore_patterns = additional_ignore_patterns

    def create_file_ignorer(self):
        if not os.path.isfile(self.gitignore_file):
            return self.additional_ignores

        with open(self.gitignore_file, "r") as file:
            lines = file.readlines()

        return FileIgnorer([line.strip() for line in lines] + self.additional_ignore_patterns)
