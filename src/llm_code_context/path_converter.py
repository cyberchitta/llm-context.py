from pathlib import Path
from typing import List


class PathConverter:
    def __init__(self, root: Path):
        self.root = root
        self.root_name = self.root.name

    def validate(self, paths: List[str]) -> bool:
        return all(path.startswith(f"/{self.root_name}/") for path in paths)

    def to_absolute(self, relative_paths: List[str]) -> List[str]:
        if not self.validate(relative_paths):
            raise ValueError("Invalid paths provided")
        return [str(self.root / Path(path[len(self.root_name) + 2 :])) for path in relative_paths]
