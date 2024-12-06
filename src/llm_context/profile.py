from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from packaging import version

from llm_context.utils import ProjectLayout, Toml, safe_read_file

CURRENT_CONFIG_VERSION = version.parse("2")

GIT_IGNORE_DEFAULT: list[str] = [
    ".git",
    ".gitignore",
    ".llm-context/",
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


@dataclass(frozen=True)
class Profile:
    name: str
    gitignores: dict[str, list[str]]
    templates: dict[str, str]
    settings: dict[str, Any]
    only_includes: dict[str, list[str]]

    @staticmethod
    def create_default() -> "Profile":
        return Profile.create(
            "default",
            {"full_files": GIT_IGNORE_DEFAULT, "outline_files": GIT_IGNORE_DEFAULT},
            {},
            {"no_media": False, "with_user_notes": False},
            {"full_files": INCLUDE_ALL, "outline_files": INCLUDE_ALL},
        )

    @staticmethod
    def create_code() -> "Profile":
        return Profile.create_default().with_name("code")

    @staticmethod
    def from_config(name, config: dict[str, Any]) -> "Profile":
        return Profile.create(
            name,
            config["gitignores"],
            config.get("templates", {}),
            config["settings"],
            config["only-include"],
        )

    @staticmethod
    def create(name, gitignores, templates, settings, only_include) -> "Profile":
        return Profile(name, gitignores, templates, settings, only_include)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.gitignores[f"{context_type}_files"]

    def get_settings(self) -> dict[str, Any]:
        return self.settings

    def get_only_includes(self, context_type: str) -> list[str]:
        return self.only_includes[f"{context_type}_files"]

    def get_template(self, template_id: str) -> Optional[str]:
        return self.templates.get(template_id)

    def get_prompt(self, project_layout: ProjectLayout) -> Optional[str]:
        prompt_file = self.get_template("prompt")
        if prompt_file:
            prompt_path = project_layout.get_template_path(prompt_file)
            return safe_read_file(str(prompt_path))
        return None

    def get_project_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.project_notes_path))

    def get_user_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.user_notes_path))

    def with_name(self, name: str) -> "Profile":
        return Profile.create(
            name, self.gitignores, self.templates, self.settings, self.only_includes
        )

    def to_dict(self) -> dict[str, Any]:
        non_optional = {
            "name": self.name,
            "gitignores": self.gitignores,
            "settings": self.settings,
            "only-include": self.only_includes,
        }
        return {**non_optional, "templates": self.templates} if self.templates else non_optional

@dataclass(frozen=True)
class ToolConstants:
    __warning__: str
    config_version: str
    default_profile: dict[str, Any]

    @staticmethod
    def load(path: Path) -> "ToolConstants":
        try:
            return ToolConstants(**Toml.load(path))
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
        return ToolConstants.create(version, Profile.create_default().to_dict())

    @staticmethod
    def create(config_version: str, default_profile: dict[str, Any]) -> "ToolConstants":
        return ToolConstants(
            "This file is managed by llm-context. DO NOT EDIT.",
            config_version,
            default_profile,
        )

    @property
    def needs_update(self) -> bool:
        return version.parse(self.config_version) < CURRENT_CONFIG_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "__warning__": self.__warning__,
            "config_version": self.config_version,
            "default_profile": self.default_profile,
        }


@dataclass(frozen=True)
class ProfileResolver:
    config: dict[str, Any]
    system_state: ToolConstants

    @staticmethod
    def create(config: dict[str, Any], system_state: ToolConstants) -> "ProfileResolver":
        return ProfileResolver(config, system_state)

    def has_profile(self, profile_name: str) -> bool:
        if profile_name == "default":
            return True
        return profile_name in self.config["profiles"]

    def get_profile(self, profile_name: str) -> Profile:
        if profile_name == "default":
            return Profile.from_config("default", self.system_state.default_profile)
        resolved_config = self.resolve_profile(profile_name)
        return Profile.from_config(profile_name, resolved_config)

    def resolve_profile(self, profile_name: str) -> dict[str, Any]:
        try:
            profile_config = self.config["profiles"][profile_name]
        except KeyError:
            raise ValueError(f"Profile '{profile_name}' not found in config")
        if "base" not in profile_config:
            return cast(dict[str, Any], profile_config)
        base_name = profile_config["base"]
        try:
            base_profile = self.resolve_profile(base_name)
        except KeyError:
            raise ValueError(
                f"Base profile '{base_name}' referenced by '{profile_name}' not found in config"
            )
        merged = base_profile.copy()
        for key, value in profile_config.items():
            if key == "base":
                continue
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged
