import os
from functools import reduce
from typing import List, Tuple


class FolderStructureDiagram:
    indent: str = "    "

    def __init__(self, root_dir: str, ignored_dirs: List[str], ignored_files: List[str]):
        self.root_dir: str = root_dir
        self.ignored_dirs: List[str] = ignored_dirs
        self.ignored_files: List[str] = ignored_files

    def is_ignored(self, name: str, is_dir: bool) -> bool:
        if is_dir:
            return any(name == d.rstrip("/") for d in self.ignored_dirs)
        else:
            return name in self.ignored_files

    def is_last(self, entries: List[str], i: int) -> bool:
        return i == len(entries) - 1

    def get_prefix(self, is_last: bool) -> str:
        return "└── " if is_last else "├── "

    def process(
        self, entries: List[str], current_dir: str, level: int, entry: str, i: int
    ) -> List[str]:
        if self.is_ignored(entry, os.path.isdir(os.path.join(current_dir, entry))):
            return []

        prefix = self.get_prefix(self.is_last(entries, i))
        entry_path = os.path.join(current_dir, entry)
        fmt_entry = f"{FolderStructureDiagram.indent * level}{prefix}{entry}"

        if os.path.isdir(entry_path):
            sub_structure = self.generate(entry_path, level + 1)
            return [f"{fmt_entry}/"] + sub_structure
        else:
            return [f"{fmt_entry}"]

    def generate(self, current_dir: str, level: int = 0) -> List[str]:
        entries = os.listdir(current_dir)
        entries.sort()

        structure = reduce(
            lambda acc, x: acc + self.process(entries, current_dir, level, x[1], x[0]),
            enumerate(entries),
            [],
        )

        return structure

    def diagram(self) -> str:
        return "\n".join(self.generate(self.root_dir))
