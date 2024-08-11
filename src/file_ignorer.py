import fnmatch
from typing import List


class FileIgnorer:
    @staticmethod
    def should_ignore(pattern: str, name: str, is_dir: bool) -> bool:
        if pattern.startswith("/") and pattern.endswith("/"):
            if is_dir:
                return fnmatch.fnmatch(name, pattern[1:-1])
            else:
                return False
        elif pattern.startswith("/"):
            if is_dir:
                return fnmatch.fnmatch(name, pattern[1:])
            else:
                return False
        elif pattern.endswith("/") and is_dir:
            return fnmatch.fnmatch(name, pattern[:-1])
        elif not pattern.endswith("/"):
            return fnmatch.fnmatch(name, pattern)
        else:
            return False

    def __init__(self, ignore_patterns: List[str]):
        self.ignore_patterns: List[str] = ignore_patterns

    def ignore(self, name: str, is_dir: bool) -> bool:
        return any(
            FileIgnorer.should_ignore(pattern, name, is_dir) for pattern in self.ignore_patterns
        )
