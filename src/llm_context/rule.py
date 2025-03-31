from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from packaging import version

from llm_context.rule_parser import RuleLoader
from llm_context.utils import ProjectLayout, Yaml, safe_read_file

CURRENT_CONFIG_VERSION = version.parse("2.8")

MEDIA_EXTENSIONS: list[str] = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".svg",
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".mp3",
    ".wav",
    ".flac",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".eot",
    ".ico",
    ".pdf",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".map",
]

GITIGNORE: list[str] = [
    ".git",
    ".gitignore",
    ".llm-context/",
    "*.tmp",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "go.sum",
    "elm-stuff",
    "LICENSE",
    "CHANGELOG.md",
    "README.md",
    ".env",
    ".dockerignore",
    "Dockerfile",
    "docker-compose.yml",
    "*.log",
    "*.svg",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.ico",
    "*.woff",
    "*.woff2",
    "*.eot",
    "*.ttf",
    "*.map",
]
IGNORE_NOTHING = [".git"]
INCLUDE_ALL = ["**/*"]


DEFAULT_GITIGNORES_PROFILE = "lc-gitignores"
DEFAULT_CODE_PROFILE = "lc-code"


@dataclass(frozen=True)
class Rule:
    name: str
    gitignores: dict[str, list[str]]
    only_includes: dict[str, list[str]]
    description: str
    files: list[str]
    rules: list[str]

    @staticmethod
    def create_code_gitignores(name: str) -> "Rule":
        media = [f"*.{ext.lstrip('.')}" for ext in MEDIA_EXTENSIONS]
        return Rule.create(
            name,
            "Base ignore patterns for code files, customize this for project-specific ignores.",
            {
                "full_files": GITIGNORE,
                "outline_files": GITIGNORE,
                "diagram_files": IGNORE_NOTHING + media,
            },
            {"full_files": INCLUDE_ALL, "outline_files": INCLUDE_ALL, "diagram_files": INCLUDE_ALL},
            [],
            [],
        )

    @staticmethod
    def create_code_dict(name: str) -> dict[str, Any]:
        return {
            "name": name,
            "description": f"Default rule for software projects, using {DEFAULT_GITIGNORES_PROFILE} base rule.",
            "base": DEFAULT_GITIGNORES_PROFILE,
            "prompt": "lc-prompt.md",
        }

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
    default_profile: dict[str, Any]

    @staticmethod
    def load(path: Path) -> "ToolConstants":
        try:
            return ToolConstants(**Yaml.load(path))
        except Exception:
            return ToolConstants.create_null()

    @staticmethod
    def create_new() -> "ToolConstants":
        return ToolConstants.create_default(str(CURRENT_CONFIG_VERSION))

    @staticmethod
    def create_null() -> "ToolConstants":
        return ToolConstants.create_default("0")

    @staticmethod
    def create_default(version: str) -> "ToolConstants":
        return ToolConstants.create(version, Rule.create_code_dict("default"))

    @staticmethod
    def create(config_version: str, default_profile: dict[str, Any]) -> "ToolConstants":
        return ToolConstants(
            "This file is managed by llm-context. DO NOT EDIT.",
            config_version,
            default_profile,
        )

    @property
    def needs_update(self) -> bool:
        return cast(bool, version.parse(self.config_version) < CURRENT_CONFIG_VERSION)

    def to_dict(self) -> dict[str, Any]:
        return {
            "__warning__": self.__warning__,
            "config_version": self.config_version,
            "default_profile": self.default_profile,
        }


@dataclass(frozen=True)
class RuleResolver:
    config: dict[str, Any]
    system_state: ToolConstants
    rule_loader: RuleLoader

    @staticmethod
    def create(
        config: dict[str, Any], system_state: ToolConstants, project_layout: ProjectLayout
    ) -> "RuleResolver":
        return RuleResolver(config, system_state, RuleLoader.create(project_layout))

    def has_profile(self, profile_name: str) -> bool:
        if profile_name == "default":
            return True
        if self.rule_loader.load_rule(profile_name):
            return True
        return profile_name in self.config["profiles"]

    def get_profile(self, profile_name: str) -> Rule:
        if profile_name == "default":
            return Rule.from_config(self.system_state.default_profile)
        if self.rule_loader:
            rule = self.rule_loader.load_rule(profile_name)
            if rule:
                return Rule.from_config(rule.to_profile_config())
        resolved_config = self.resolve_profile(profile_name)
        return Rule.from_config(resolved_config)

    def resolve_profile(self, profile_name: str) -> dict[str, Any]:
        if profile_name == "default":
            return self.system_state.default_profile
        try:
            profile_config = self.config["profiles"][profile_name]
        except KeyError:
            raise ValueError(f"Rule '{profile_name}' not found in config")
        if "base" not in profile_config:
            return cast(dict[str, Any], profile_config)
        base_name = profile_config["base"]
        try:
            base_profile = self.resolve_profile(base_name)
        except KeyError:
            raise ValueError(
                f"Base rule '{base_name}' referenced by '{profile_name}' not found in config"
            )
        merged = base_profile.copy()
        for key, value in profile_config.items():
            if key == "base":
                continue
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = {**merged[key], **value}
            elif isinstance(value, list) and key in merged and isinstance(merged[key], list):
                if key in ["file-references", "rule-references"]:
                    merged[key] = merged[key] + value
                else:
                    merged[key] = value
            else:
                merged[key] = value
        return merged
