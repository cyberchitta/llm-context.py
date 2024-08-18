import os
from typing import List

from pathspec import GitIgnoreSpec


class PathspecIgnorer:
    @staticmethod
    def create(ignore_patterns: List[str]) -> "PathspecIgnorer":
        pathspec = GitIgnoreSpec.from_lines(ignore_patterns)
        return PathspecIgnorer(pathspec)

    def __init__(self, pathspec: GitIgnoreSpec):
        self.pathspec = pathspec

    def ignore(self, path: str) -> bool:
        assert path not in ("/", ""), "Root directory cannot be an input for ignore method"
        return self.pathspec.match_file(path)
