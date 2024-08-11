import os
import fnmatch
from typing import List


class PathIgnorer:
    @classmethod
    def create(cls, ignore_patterns: List[str]) -> "PathIgnorer":
        return cls(
            [
                pattern.rstrip()
                for pattern in ignore_patterns
                if pattern and not pattern.startswith("#")
            ]
        )

    def __init__(self, ignore_patterns: List[str]):
        self.ignore_patterns = ignore_patterns

    def ignore(self, path: str, is_dir: bool) -> bool:
        path = path.rstrip(os.sep)
        return any(self._should_ignore(pattern, path, is_dir) for pattern in self.ignore_patterns)

    def _should_ignore(self, pattern: str, path: str, is_dir: bool) -> bool:
        if pattern.endswith("/") and not is_dir:
            return False

        if pattern.startswith("/"):
            return self._match_from_root(pattern, path)
        else:
            return self._match_pattern(pattern, path)

    def _match_from_root(self, pattern: str, path: str) -> bool:
        pattern = pattern.lstrip("/")
        path_parts = path.split(os.sep)
        return any(
            fnmatch.fnmatch("/".join(path_parts[i:]), pattern) for i in range(len(path_parts))
        )

    def _match_pattern(self, pattern: str, path: str) -> bool:
        path_parts = path.split(os.sep)
        return any(
            fnmatch.fnmatch("/".join(path_parts[i:]), f"**/{pattern}")
            for i in range(len(path_parts))
        )
