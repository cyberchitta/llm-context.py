from dataclasses import dataclass
from pathlib import Path

from llm_context.utils import Toml


@dataclass(frozen=True)
class FileSelection:
    profile: str
    full_files: list[str]
    outline_files: list[str]

    @staticmethod
    def create_default() -> "FileSelection":
        return FileSelection.create("code", [], [])

    @staticmethod
    def create(profile: str, full_files: list[str], outline_files: list[str]) -> "FileSelection":
        return FileSelection(profile, full_files, outline_files)

    def with_profile(self, profile: str) -> "FileSelection":
        return FileSelection.create(profile, self.full_files, self.outline_files)


@dataclass(frozen=True)
class StateStore:
    storage_path: Path

    def load(self) -> FileSelection:
        data = Toml.load(self.storage_path)
        return FileSelection.create(
            data.get("profile", "code"),
            data.get("file_lists", {}).get("full", []),
            data.get("file_lists", {}).get("outline", []),
        )

    def save(self, state: FileSelection):
        data = {
            "profile": state.profile,
            "file_lists": {"full": state.full_files, "outline": state.outline_files},
        }
        Toml.save(self.storage_path, data)
