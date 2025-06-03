from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from packaging import version

from llm_context.rule_parser import RuleLoader, RuleParser
from llm_context.utils import ProjectLayout, Yaml, safe_read_file

CURRENT_CONFIG_VERSION = version.parse("3.2")

IGNORE_NOTHING = [".git"]
INCLUDE_ALL = ["**/*"]


DEFAULT_CODE_RULE = "lc-code"


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    gitignores: dict[str, list[str]]
    only_includes: dict[str, list[str]]
    files: list[str]
    rules: list[str]

    @staticmethod
    def from_config(config: dict[str, Any]) -> "Rule":
        return Rule.create(
            config.get("name", ""),
            config.get("description", ""),
            config.get("gitignores", {}),
            config.get("only-include", {}),
            config.get("files", []),
            config.get("rules", []),
        )

    @staticmethod
    def create(name, description, gitignores, only_include, files, rules) -> "Rule":
        return Rule(name, description, gitignores, only_include, files, rules)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.gitignores.get(f"{context_type}_files", IGNORE_NOTHING)

    def get_only_includes(self, context_type: str) -> list[str]:
        return self.only_includes.get(f"{context_type}_files", INCLUDE_ALL)

    def get_prompt(self, project_layout: ProjectLayout) -> Optional[str]:
        if not self.name:
            return None
        from llm_context.rule_parser import RuleProvider

        content = RuleProvider.create(project_layout).get_rule_content(self.name)
        return content if content else None

    def get_project_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.project_notes_path))

    def get_user_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.user_notes_path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            **({"gitignores": self.gitignores} if self.gitignores else {}),
            **({"only-include": self.only_includes} if self.only_includes else {}),
            **({"files": self.files} if self.files else {}),
            **({"rules": self.rules} if self.rules else {}),
        }


@dataclass(frozen=True)
class ToolConstants:
    __warning__: str
    config_version: str

    @staticmethod
    def load(path: Path) -> "ToolConstants":
        try:
            return ToolConstants(**Yaml.load(path))
        except Exception:
            return ToolConstants.create_null()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ToolConstants":
        return ToolConstants.create(data.get("config_version", "0"))

    @staticmethod
    def create_new() -> "ToolConstants":
        return ToolConstants.create_default(str(CURRENT_CONFIG_VERSION))

    @staticmethod
    def create_null() -> "ToolConstants":
        return ToolConstants.create_default("0")

    @staticmethod
    def create_default(version: str) -> "ToolConstants":
        return ToolConstants.create(version)

    @staticmethod
    def create(config_version: str) -> "ToolConstants":
        return ToolConstants("This file is managed by llm-context. DO NOT EDIT.", config_version)

    @property
    def needs_update(self) -> bool:
        return cast(bool, version.parse(self.config_version) < CURRENT_CONFIG_VERSION)

    def to_dict(self) -> dict[str, Any]:
        return {"__warning__": self.__warning__, "config_version": self.config_version}


@dataclass(frozen=True)
class RuleResolver:
    system_state: ToolConstants
    rule_loader: RuleLoader

    @staticmethod
    def create(system_state: ToolConstants, project_layout: ProjectLayout) -> "RuleResolver":
        rule_loader = RuleLoader.create(project_layout)
        return RuleResolver(system_state, rule_loader)

    def has_rule(self, rule_name: str) -> bool:
        return self.rule_loader.load_rule(rule_name) is not None

    def get_rule(self, rule_name: str) -> Rule:
        rule = self.rule_loader.load_rule(rule_name)
        if "base" in rule.frontmatter:
            base_name = rule.frontmatter["base"]
            base_profile = self.get_rule(base_name)
            base_dict = base_profile.to_dict()
            rule_dict = {k: v for k, v in rule.frontmatter.items() if k != "base"}
            merged = self._merge_rule_dicts(base_dict, rule_dict)
            merged_rule = RuleParser(merged, rule.content, rule.path)
            return Rule.from_config(merged_rule.to_rule_config())
        return Rule.from_config(rule.to_rule_config())

    def _merge_rule_dicts(
        self, base_dict: dict[str, Any], override_dict: dict[str, Any]
    ) -> dict[str, Any]:
        merged = base_dict.copy()
        for key, value in override_dict.items():
            if key == "base":
                continue
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = {**merged[key], **value}
            elif isinstance(value, list) and key in merged and isinstance(merged[key], list):
                if key in ["files", "rules"]:
                    merged[key] = merged[key] + value
                else:
                    merged[key] = value
            else:
                merged[key] = value
        return merged
