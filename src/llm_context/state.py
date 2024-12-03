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
class AllSelections:
    selections: dict[str, FileSelection]

    @staticmethod
    def create_empty() -> "AllSelections":
        return AllSelections({})

    def get_selection(self, profile: str) -> FileSelection:
        return self.selections.get(profile, FileSelection.create(profile, [], []))

    def with_selection(self, selection: FileSelection) -> "AllSelections":
        new_selections = dict(self.selections)
        new_selections[selection.profile] = selection
        return AllSelections(new_selections)


@dataclass(frozen=True)
class StateStore:
    storage_path: Path

    def load(self) -> AllSelections:
        try:
            data = Toml.load(self.storage_path)
            selections = {}
            for profile, sel_data in data.get("selections", {}).items():
                selections[profile] = FileSelection.create(
                    profile, sel_data.get("full_files", []), sel_data.get("outline_files", [])
                )
            return AllSelections(selections)
        except Exception:
            return AllSelections.create_empty()

    def save(self, store: AllSelections):
        data = {
            "selections": {
                profile: {"full_files": sel.full_files, "outline_files": sel.outline_files}
                for profile, sel in store.selections.items()
            }
        }
        Toml.save(self.storage_path, data)
