import fnmatch


class FileIgnorer:
    @staticmethod
    def should_ignore(pattern, name, is_dir):
        if pattern.endswith("/") and is_dir:
            return fnmatch.fnmatch(name, pattern[:-1])
        elif not pattern.endswith("/"):
            return fnmatch.fnmatch(name, pattern)
        else:
            return False

    def __init__(self, ignore_patterns):
        self.ignore_patterns = ignore_patterns

    def ignore(self, name, is_dir):
        return any(
            FileIgnorer.should_ignore(pattern, name, is_dir) for pattern in self.ignore_patterns
        )
