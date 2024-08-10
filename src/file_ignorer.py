import os
from fnmatch import fnmatch
from typing import List


class FileIgnorer:
    @classmethod
    def create(cls, ignore_patterns: List[str]) -> "FileIgnorer":
        ignore_patterns_list = []
        negation_patterns_list = []
        for pattern in ignore_patterns:
            pattern = pattern.rstrip()  # Remove trailing spaces
            if pattern and not pattern.startswith("#"):
                if pattern.startswith("!"):
                    negation_patterns_list.append(pattern[1:])
                else:
                    ignore_patterns_list.append(pattern)
        return cls(ignore_patterns_list, negation_patterns_list)

    def __init__(self, ignore_patterns: List[str], negation_patterns: List[str]):
        self.ignore_patterns = ignore_patterns
        self.negation_patterns = negation_patterns

    def ignore(self, path: str, is_dir: bool) -> bool:
        path = path.rstrip(os.sep)
        name = os.path.basename(path)

        # Check ignore patterns first
        ignored = any(
            self._match_pattern(pattern, path, name, is_dir) for pattern in self.ignore_patterns
        )

        # Then check negation patterns
        if ignored:
            negated = any(
                self._match_pattern(pattern, path, name, is_dir)
                for pattern in self.negation_patterns
            )
            return not negated

        return ignored

    def _match_pattern(self, pattern: str, path: str, name: str, is_dir: bool) -> bool:
        if pattern.endswith("/"):
            if not is_dir:
                return False
            pattern = pattern[:-1]

        if pattern.startswith("/"):
            return self._fnmatch_with_separators(path, pattern[1:])
        elif "/" in pattern:
            return self._fnmatch_with_separators(path, f"**/{pattern}")
        else:
            return fnmatch(name, pattern) or self._fnmatch_with_separators(path, f"**/{pattern}")

    def _fnmatch_with_separators(self, path: str, pattern: str) -> bool:
        path_parts = path.split(os.sep)
        pattern_parts = pattern.split("/")

        return self._match_parts(path_parts, pattern_parts)

    def _match_parts(self, path_parts: List[str], pattern_parts: List[str]) -> bool:
        if not pattern_parts:
            return not path_parts

        if not path_parts:
            return all(part == "**" for part in pattern_parts)

        if pattern_parts[0] == "**":
            if len(pattern_parts) == 1:
                return True
            for i in range(len(path_parts) + 1):
                if self._match_parts(path_parts[i:], pattern_parts[1:]):
                    return True
            return False

        if fnmatch(path_parts[0], pattern_parts[0]):
            return self._match_parts(path_parts[1:], pattern_parts[1:])

        return False
