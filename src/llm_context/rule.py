from dataclasses import dataclass
from logging import WARNING
from pathlib import Path
from typing import Any, Optional, cast

from packaging import version

from llm_context.exceptions import RuleResolutionError
from llm_context.rule_parser import DEFAULT_CODE_RULE, RuleLoader, RuleParser
from llm_context.utils import ProjectLayout, Yaml, log, safe_read_file

CURRENT_CONFIG_VERSION = version.parse("5.1")

IGNORE_NOTHING = [".git"]
INCLUDE_ALL = ["**/*"]

DEFAULT_OVERVIEW_MODE = "full"


@dataclass(frozen=True)
class RuleComposition:
    filters: list[str]
    excerpters: list[str]

    @staticmethod
    def from_config(config: dict[str, Any]) -> "RuleComposition":
        return RuleComposition(
            config.get("filters", []),
            config.get("excerpters", []),
        )


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    overview: str
    instructions: str
    compose: RuleComposition
    gitignores: dict[str, list[str]]
    limit_to: dict[str, list[str]]
    also_include: dict[str, list[str]]
    implementations: list[tuple[str, str]]  # (file_path, definition_name)
    excerpt_modes: dict[str, str]
    excerpt_config: dict[str, dict[str, Any]]

    @staticmethod
    def from_config(config: dict[str, Any]) -> "Rule":
        return Rule.create(
            config.get("name", ""),
            config.get("description", ""),
            config.get("overview", DEFAULT_OVERVIEW_MODE),
            config.get("instructions", ""),
            RuleComposition.from_config(config.get("compose", {})),
            config.get("gitignores", {}),
            config.get("limit-to", {}),
            config.get("also-include", {}),
            [tuple(impl) for impl in config.get("implementations", [])],
            config.get("excerpt-modes", {}),
            config.get("excerpt-config", {}),
        )

    @staticmethod
    def create(
        name,
        description,
        overview,
        instructions,
        compose,
        gitignores,
        limit_to,
        also_include,
        implementations,
        excerpt_modes,
        excerpt_config,
    ) -> "Rule":
        return Rule(
            name,
            description,
            overview,
            instructions,
            compose,
            gitignores,
            limit_to,
            also_include,
            implementations,
            excerpt_modes,
            excerpt_config,
        )

    def get_excerpt_mode(self, rel_path: str) -> Optional[str]:
        import fnmatch

        for pattern, mode in self.excerpt_modes.items():
            if fnmatch.fnmatch(rel_path, pattern):
                return mode
        return None

    def get_excerpt_config(self, excerpter_name: str) -> dict[str, Any]:
        return self.excerpt_config.get(excerpter_name, {})

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.gitignores.get(f"{context_type}-files", IGNORE_NOTHING)

    def get_limit_to_patterns(self, context_type: str) -> list[str]:
        return self.limit_to.get(f"{context_type}-files", INCLUDE_ALL)

    def get_also_include_patterns(self, context_type: str) -> list[str]:
        return self.also_include.get(f"{context_type}-files", [])

    def get_instructions(self) -> Optional[str]:
        return self.instructions if self.instructions else None

    def get_project_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.project_notes_path))

    def get_user_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.user_notes_path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "overview": self.overview,
            "instructions": self.instructions,
            "compose": {
                "filters": self.compose.filters,
                "excerpters": self.compose.excerpters,
            }
            if any([self.compose.filters, self.compose.excerpters])
            else {},
            **({"gitignores": self.gitignores} if self.gitignores else {}),
            **({"limit-to": self.limit_to} if self.limit_to else {}),
            **({"also-include": self.also_include} if self.also_include else {}),
            **({"implementations": self.implementations} if self.implementations else {}),
            **({"excerpt-modes": self.excerpt_modes} if self.excerpt_modes else {}),
            **({"excerpt-config": self.excerpt_config} if self.excerpt_config else {}),
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
    _composition_stack: frozenset[str] = frozenset()

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
        if rule_name in self._composition_stack:
            raise ValueError(
                f"Circular composition detected: {' -> '.join(self._composition_stack)} -> {rule_name}"
            )
        try:
            rule = self.rule_loader.load_rule(rule_name)
            composed_config = self._compose_rule_config(rule, rule_name)
            return Rule.from_config(composed_config)
        except RuleResolutionError:
            raise
        except Exception as e:
            raise RuleResolutionError(
                f"Failed to resolve rule '{rule_name}': {str(e)}. "
                f"This may indicate outdated rule syntax or missing dependencies. "
                f"Consider updating the rule or switching to '{DEFAULT_CODE_RULE}' with: lc-set-rule {DEFAULT_CODE_RULE}"
            )

    def _compose_rule_config(self, rule: RuleParser, rule_name: str) -> dict[str, Any]:
        new_resolver = RuleResolver(
            self.system_state, self.rule_loader, self._composition_stack | {rule_name}
        )
        resolved_instructions = ""
        if "instructions" in rule.frontmatter:
            if rule.content.strip():
                log(
                    WARNING,
                    f"Rule '{rule_name}' has both 'instructions' field and markdown content. The markdown content will be ignored.",
                )
            instruction_contents = []
            for instruction_rule_name in rule.frontmatter["instructions"]:
                instruction_rule_parser = new_resolver.rule_loader.load_rule(instruction_rule_name)
                if instruction_rule_parser.content.strip():
                    instruction_contents.append(instruction_rule_parser.content)
            resolved_instructions = "\n\n".join(instruction_contents)
        else:
            resolved_instructions = rule.content
        if not rule.frontmatter.get("compose"):
            config = rule.to_rule_config()
            config["instructions"] = resolved_instructions
            return config
        composed_config = {
            "name": rule.name,
            "description": rule.frontmatter.get("description", ""),
            "overview": rule.frontmatter.get("overview", DEFAULT_OVERVIEW_MODE),
            "instructions": resolved_instructions,
            "gitignores": {},
            "limit-to": {},
            "also-include": {},
            "implementations": [],
            "excerpt-modes": {},
            "excerpt-config": {},
        }
        compose_config = rule.frontmatter.get("compose", {})
        for filter_rule_name in compose_config.get("filters", []):
            composed_filter_rule = new_resolver.get_rule(filter_rule_name)
            filter_config = composed_filter_rule.to_dict()
            self._merge_gitignores(composed_config, filter_config)
            self._merge_limit_to(composed_config, filter_config)
            self._merge_also_include(composed_config, filter_config)
        for excerpter_rule_name in compose_config.get("excerpters", []):
            composed_excerpter_rule = new_resolver.get_rule(excerpter_rule_name)
            excerpter_config = composed_excerpter_rule.to_dict()
            self._merge_excerpt_modes(composed_config, excerpter_config)
            self._merge_excerpt_config(composed_config, excerpter_config)
        for field in [
            "gitignores",
            "limit-to",
            "also-include",
            "implementations",
            "excerpt-modes",
            "excerpt-config",
        ]:
            if field in rule.frontmatter:
                if field == "gitignores":
                    self._merge_gitignores(composed_config, rule.frontmatter)
                elif field == "limit-to":
                    self._merge_limit_to(composed_config, rule.frontmatter)
                elif field == "also-include":
                    self._merge_also_include(composed_config, rule.frontmatter)
                elif field == "excerpt-modes":
                    self._merge_excerpt_modes(composed_config, rule.frontmatter)
                elif field == "excerpt-config":
                    self._merge_excerpt_config(composed_config, rule.frontmatter)
                else:
                    composed_config[field].extend(rule.frontmatter[field])
        return composed_config

    def _merge_gitignores(self, target: dict, source: dict):
        source_gitignores = source.get("gitignores", {})
        for key, patterns in source_gitignores.items():
            if key not in target["gitignores"]:
                target["gitignores"][key] = []
            existing = set(target["gitignores"][key])
            target["gitignores"][key].extend([p for p in patterns if p not in existing])

    def _merge_limit_to(self, target: dict, source: dict):
        source_includes = source.get("limit-to", {})
        for key, patterns in source_includes.items():
            if key in target["limit-to"] and target["limit-to"][key]:
                log(
                    WARNING,
                    f"Multiple 'limit-to' clauses for '{key}' detected. "
                    f"Keeping patterns: {target['limit-to'][key]}. "
                    f"Dropping patterns: {patterns}.",
                )
                continue
            target["limit-to"][key] = list(patterns)

    def _merge_also_include(self, target: dict, source: dict):
        source_includes = source.get("also-include", {})
        for key, patterns in source_includes.items():
            if key not in target["also-include"]:
                target["also-include"][key] = []
            existing = set(target["also-include"][key])
            target["also-include"][key].extend([p for p in patterns if p not in existing])

    def _merge_excerpt_modes(self, target: dict, source: dict):
        source_modes = source.get("excerpt-modes", {})
        for pattern, mode in source_modes.items():
            if pattern not in target["excerpt-modes"]:
                target["excerpt-modes"][pattern] = mode

    def _merge_excerpt_config(self, target: dict, source: dict):
        source_configs = source.get("excerpt-config", {})
        for processor_name, processor_config in source_configs.items():
            if processor_name not in target["excerpt-config"]:
                target["excerpt-config"][processor_name] = {}
            existing = target["excerpt-config"][processor_name]
            existing.update(processor_config)
