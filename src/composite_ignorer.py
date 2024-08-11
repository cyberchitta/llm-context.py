import os
from typing import List
from file_ignorer import FileIgnorer
from path_ignorer import PathIgnorer

class CompositeIgnorer:
    @staticmethod
    def is_valid_pattern(pattern: str) -> bool:
        return '//' not in pattern and not pattern.startswith('#') and pattern.strip()

    @classmethod
    def create(cls, ignore_patterns: List[str]) -> 'CompositeIgnorer':
        valid_patterns = [pattern.strip() for pattern in ignore_patterns if cls.is_valid_pattern(pattern)]
        if len(valid_patterns) != len(ignore_patterns):
            invalid_patterns = set(ignore_patterns) - set(valid_patterns)
            raise ValueError(f"Invalid patterns detected: {invalid_patterns}")
        file_ignorer = FileIgnorer(valid_patterns)
        path_ignorer = PathIgnorer(valid_patterns)
        return cls(file_ignorer, path_ignorer)

    def __init__(self, file_ignorer: FileIgnorer, path_ignorer: PathIgnorer):
        self.file_ignorer = file_ignorer
        self.path_ignorer = path_ignorer

    def ignore(self, path: str, basename: str, is_dir: bool) -> bool:
        return self.file_ignorer.ignore(basename, is_dir) or self.path_ignorer.ignore(path, is_dir)