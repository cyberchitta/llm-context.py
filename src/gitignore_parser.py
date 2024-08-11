import os
from composite_ignorer import CompositeIgnorer

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

    def create_composite_ignorer(self):
        patterns = self.additional_ignore_patterns.copy()
        if os.path.isfile(self.gitignore_file):
            with open(self.gitignore_file, "r") as file:
                patterns.extend(file.read().splitlines())
        
        try:
            return CompositeIgnorer.create(patterns)
        except ValueError as e:
            print(f"Error creating CompositeIgnorer: {e}")
            print("Falling back to using only valid patterns.")
            valid_patterns = [p for p in patterns if CompositeIgnorer.is_valid_pattern(p)]
            return CompositeIgnorer.create(valid_patterns)