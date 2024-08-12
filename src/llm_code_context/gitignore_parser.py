import os

from llm_code_context.pathspec_ignorer import PathspecIgnorer


class GitignoreParser:
    @staticmethod
    def create_default(root_directory):
        additional_ignore_patterns = [".git"]
        return GitignoreParser.create(root_directory, additional_ignore_patterns)

    @staticmethod
    def create(root_directory, additional_ignore_patterns):
        gitignore_file = os.path.join(root_directory, ".gitignore")
        return GitignoreParser(gitignore_file, additional_ignore_patterns)

    def __init__(self, gitignore_file, additional_ignore_patterns):
        self.gitignore_file = gitignore_file
        self.additional_ignore_patterns = additional_ignore_patterns

    def create_path_ignorer(self):
        patterns = self.additional_ignore_patterns.copy()
        if os.path.isfile(self.gitignore_file):
            with open(self.gitignore_file, "r") as file:
                patterns.extend(file.read().splitlines())

        return PathspecIgnorer.create(patterns)
