import os
from typing import List

from pathspec import GitIgnoreSpec


class PathspecIgnorer:
    @classmethod
    def create(cls, ignore_patterns: List[str]) -> "PathspecIgnorer":
        return cls(ignore_patterns)

    def __init__(self, ignore_patterns: List[str]):
        self.pathspec = GitIgnoreSpec.from_lines(ignore_patterns)

    def ignore(self, path: str) -> bool:
        assert path not in ("/", ""), "Root directory cannot be an input for ignore method"
        return self.pathspec.match_file(path)
