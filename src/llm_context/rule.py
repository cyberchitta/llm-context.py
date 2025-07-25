from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from packaging import version

from llm_context.rule_parser import RuleLoader, RuleParser
from llm_context.utils import ProjectLayout, Yaml, safe_read_file

CURRENT_CONFIG_VERSION = version.parse("3.4")

IGNORE_NOTHING = [".git"]
INCLUDE_ALL = ["**/*"]


DEFAULT_CODE_RULE = "lc-code"


@dataclass(frozen=True)
class RuleComposition:
    filters: list[str]
    files: list[str]
    outlines: list[str]
    implementations: list[str]
    rules: list[str]

    @staticmethod
    def from_config(config: dict[str, Any]) -> "RuleComposition":
        return RuleComposition(
            config.get("filters", []),
            config.get("files", []),
            config.get("outlines", []),
            config.get("implementations", []),
            config.get("rules", []),
        )


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    compose: RuleComposition
    gitignores: dict[str, list[str]]
    only_includes: dict[str, list[str]]
    files: list[str]
    outlines: list[str]
    implementations: list[tuple[str, str]]  # (file_path, definition_name)
    rules: list[str]

    @staticmethod
    def from_config(config: dict[str, Any]) -> "Rule":
        return Rule.create(
            config.get("name", ""),
            config.get("description", ""),
            RuleComposition.from_config(config.get("compose", {})),
            config.get("gitignores", {}),
            config.get("only-include", {}),
            config.get("files", []),
            config.get("outlines", []),
            [tuple(impl) for impl in config.get("implementations", [])],
            config.get("rules", []),
        )

    @staticmethod
    def create(
        name,
        description,
        compose,
        gitignores,
        only_include,
        files,
        outlines,
        implementations,
        rules,
    ) -> "Rule":
        return Rule(
            name,
            description,
            compose,
            gitignores,
            only_include,
            files,
            outlines,
            implementations,
            rules,
        )

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
            "compose": {
                "filters": self.compose.filters,
                "files": self.compose.files,
                "outlines": self.compose.outlines,
                "implementations": self.compose.implementations,
                "rules": self.compose.rules,
            }
            if any(
                [
                    self.compose.filters,
                    self.compose.files,
                    self.compose.outlines,
                    self.compose.implementations,
                    self.compose.rules,
                ]
            )
            else {},
            **({"gitignores": self.gitignores} if self.gitignores else {}),
            **({"only-include": self.only_includes} if self.only_includes else {}),
            **({"files": self.files} if self.files else {}),
            **({"outlines": self.outlines} if self.outlines else {}),
            **({"implementations": self.implementations} if self.implementations else {}),
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
        try:
            self.rule_loader.load_rule(rule_name)
            return True
        except Exception:
            return False

    def get_rule(self, rule_name: str) -> Rule:
        rule = self.rule_loader.load_rule(rule_name)
        composed_rule = self._compose_rule(rule)
        return Rule.from_config(composed_rule.to_rule_config())

    def _compose_rule(self, rule: RuleParser) -> RuleParser:
        if not rule.frontmatter.get("compose"):
            return rule
        composed_config = {
            "name": rule.name,
            "description": rule.frontmatter.get("description", ""),
            "gitignores": {},
            "only-include": {},
            "files": [],
            "outlines": [],
            "implementations": [],
            "rules": [],
        }
        compose_config = rule.frontmatter.get("compose", {})
        for filter_rule_name in compose_config.get("filters", []):
            filter_rule = self.rule_loader.load_rule(filter_rule_name)
            filter_config = filter_rule.frontmatter
            self._merge_gitignores(composed_config, filter_config)
            self._merge_only_includes(composed_config, filter_config)
        for rule_name in compose_config.get("rules", []):
            self.rule_loader.load_rule(rule_name)
            composed_config["rules"].append(rule_name)
        for field in [
            "gitignores",
            "only-include",
            "files",
            "outlines",
            "implementations",
            "rules",
        ]:
            if field in rule.frontmatter:
                if field in ["gitignores", "only-include"]:
                    if field == "gitignores":
                        self._merge_gitignores(composed_config, rule.frontmatter)
                    else:
                        self._merge_only_includes(composed_config, rule.frontmatter)
                else:
                    composed_config[field].extend(rule.frontmatter[field])
        return RuleParser(composed_config, rule.content, rule.path)

    def _merge_gitignores(self, target: dict, source: dict):
        source_gitignores = source.get("gitignores", {})
        for key, patterns in source_gitignores.items():
            if key not in target["gitignores"]:
                target["gitignores"][key] = []
            target["gitignores"][key].extend(patterns)

    def _merge_only_includes(self, target: dict, source: dict):
        source_includes = source.get("only-include", {})
        for key, patterns in source_includes.items():
            if key not in target["only-include"]:
                target["only-include"][key] = []
            target["only-include"][key].extend(patterns)
