import os
from typing import List, Tuple

from llm_code_context.pathspec_ignorer import PathspecIgnorer


class GitIgnorer:
    @staticmethod
    def from_git_root(root_dir: str, xtra_root_patterns: List[str] = None) -> "GitIgnorer":
        ignorer_data = [("/", PathspecIgnorer.create(xtra_root_patterns or []))]
        gitignores = GitIgnorer._collect_gitignores(root_dir)
        for relative_path, patterns in gitignores:
            ignorer_data.append((relative_path, PathspecIgnorer.create(patterns)))
        return GitIgnorer(ignorer_data)

    @staticmethod
    def _collect_gitignores(top) -> List[Tuple[str, List[str]]]:
        gitignores = []
        for root, _, files in os.walk(top):
            if ".gitignore" in files:
                with open(os.path.join(root, ".gitignore"), "r") as file:
                    patterns = file.read().splitlines()
                relpath = os.path.relpath(root, top)
                fixpath = "/" if relpath == "." else f"/{os.path.relpath(root, top)}"
                gitignores.append((fixpath, patterns))
        return gitignores

    def __init__(self, ignorer_data: List[Tuple[str, PathspecIgnorer]]):
        self.ignorer_data = ignorer_data

    def ignore(self, path: str) -> bool:
        assert path not in ("/", ""), "Root directory cannot be an input for ignore method"
        for prefix, ignorer in self.ignorer_data:
            if path.startswith(prefix):
                if ignorer.ignore(path):
                    return True
        return False
