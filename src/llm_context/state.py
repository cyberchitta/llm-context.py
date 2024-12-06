from dataclasses import dataclass
from pathlib import Path

from llm_context.utils import Toml


@dataclass(frozen=True)
class FileSelection:
    profile_name: str
    full_files: list[str]
    outline_files: list[str]

    @staticmethod
    def create_default() -> "FileSelection":
        return FileSelection.create("code", [], [])

    @staticmethod
    def create(
        profile_name: str, full_files: list[str], outline_files: list[str]
    ) -> "FileSelection":
        return FileSelection(profile_name, full_files, outline_files)

    def with_profile(self, profile_name: str) -> "FileSelection":
        return FileSelection.create(profile_name, self.full_files, self.outline_files)


@dataclass(frozen=True)
class AllSelections:
    selections: dict[str, FileSelection]

    @staticmethod
    def create_empty() -> "AllSelections":
        return AllSelections({})

    def get_selection(self, profile_name: str) -> FileSelection:
        return self.selections.get(profile_name, FileSelection.create(profile_name, [], []))

    def with_selection(self, selection: FileSelection) -> "AllSelections":
        new_selections = dict(self.selections)
        new_selections[selection.profile_name] = selection
        return AllSelections(new_selections)


@dataclass(frozen=True)
class StateStore:
    storage_path: Path

    def load(self) -> tuple[AllSelections, str]:
        try:
            data = Toml.load(self.storage_path)
            selections = {}
            for profile_name, sel_data in data.get("selections", {}).items():
                selections[profile_name] = FileSelection.create(
                    profile_name, sel_data.get("full_files", []), sel_data.get("outline_files", [])
                )
            return AllSelections(selections), data.get("current_profile", "code")
        except Exception:
            return AllSelections.create_empty(), "code"

    def save(self, store: AllSelections, current_profile: str):
        data = {
            "current_profile": current_profile,
            "selections": {
                profile_name: {"full_files": sel.full_files, "outline_files": sel.outline_files}
                for profile_name, sel in store.selections.items()
            },
        }
        Toml.save(self.storage_path, data)
