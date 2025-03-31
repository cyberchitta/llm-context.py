from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from llm_context.rule import DEFAULT_CODE_RULE
from llm_context.utils import Yaml


@dataclass(frozen=True)
class FileSelection:
    rule_name: str
    full_files: list[str]
    outline_files: list[str]
    timestamp: float

    @staticmethod
    def create_default() -> "FileSelection":
        return FileSelection.create(DEFAULT_CODE_RULE, [], [])

    @staticmethod
    def create(rule_name: str, full_files: list[str], outline_files: list[str]) -> "FileSelection":
        return FileSelection._create(
            rule_name, full_files, outline_files, datetime.now().timestamp()
        )

    @staticmethod
    def _create(
        rule_name: str, full_files: list[str], outline_files: list[str], timestamp: float
    ) -> "FileSelection":
        return FileSelection(rule_name, full_files, outline_files, timestamp)

    @property
    def files(self) -> list[str]:
        return self.full_files + self.outline_files

    def with_rule(self, rule_name: str) -> "FileSelection":
        return FileSelection.create(rule_name, self.full_files, self.outline_files)

    def with_now(self) -> "FileSelection":
        return FileSelection.create(self.rule_name, self.full_files, self.outline_files)


@dataclass(frozen=True)
class AllSelections:
    selections: dict[str, FileSelection]

    @staticmethod
    def create_empty() -> "AllSelections":
        return AllSelections({})

    def get_selection(self, rule_name: str) -> FileSelection:
        return self.selections.get(rule_name, FileSelection.create(rule_name, [], []))

    def with_selection(self, selection: FileSelection) -> "AllSelections":
        new_selections = dict(self.selections)
        new_selections[selection.rule_name] = selection
        return AllSelections(new_selections)


@dataclass(frozen=True)
class StateStore:
    storage_path: Path

    def load(self) -> tuple[AllSelections, str]:
        try:
            data = Yaml.load(self.storage_path)
            selections = {}
            for rule_name, sel_data in data.get("selections", {}).items():
                selections[rule_name] = FileSelection._create(
                    rule_name,
                    sel_data.get("full_files", []),
                    sel_data.get("outline_files", []),
                    sel_data.get("timestamp", datetime.now().timestamp()),
                )
            return AllSelections(selections), data.get("current_profile", DEFAULT_CODE_RULE)
        except Exception:
            return AllSelections.create_empty(), DEFAULT_CODE_RULE

    def save(self, store: AllSelections, current_profile: str):
        data = {
            "current_profile": current_profile,
            "selections": {
                rule_name: {
                    "full_files": sel.full_files,
                    "outline_files": sel.outline_files,
                    "timestamp": sel.timestamp,
                }
                for rule_name, sel in store.selections.items()
            },
        }
        Yaml.save(self.storage_path, data)
