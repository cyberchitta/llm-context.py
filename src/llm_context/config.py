from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from packaging import version

from llm_context.utils import safe_read_file

PROJECT_INFO: str = (
    "This project uses llm-context. For more information, visit: "
    "https://github.com/cyberchitta/llm-context.py or "
    "https://pypi.org/project/llm-context/"
)
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
CURRENT_CONFIG_VERSION = version.parse("2")


@dataclass(frozen=True)
class ProjectLayout:
    root_path: Path

    @property
    def config_path(self) -> Path:
        return self.root_path / ".llm-context" / "config.toml"

    @property
    def state_path(self) -> Path:
        return self.root_path / ".llm-context" / "lc-state.toml"

    @property
    def state_store_path(self) -> Path:
        return self.root_path / ".llm-context" / "curr_ctx.toml"

    @property
    def templates_path(self) -> Path:
        return self.root_path / ".llm-context" / "templates"

    def get_template_path(self, template_name: str) -> Path:
        return self.templates_path / template_name


@dataclass(frozen=True)
class Profile:
    name: str
    gitignores: dict[str, list[str]]
    templates: dict[str, str]
    settings: dict[str, Any]

    @staticmethod
    def create_default() -> "Profile":
        return Profile.create(
            "default",
            {"full_files": GIT_IGNORE_DEFAULT, "outline_files": GIT_IGNORE_DEFAULT},
            {"prompt": "lc-prompt.md"},
            {"with_prompt": False, "no_media": False},
        )

    @staticmethod
    def create_code() -> "Profile":
        return Profile.create_default().with_name("code")

    @staticmethod
    def from_config(name, config: dict[str, Any]) -> "Profile":
        return Profile.create(name, config["gitignores"], config["templates"], config["settings"])

    @staticmethod
    def create(name, gitignores, templates, settings) -> "Profile":
        return Profile(name, gitignores, templates, settings)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.gitignores.get(f"{context_type}_files", [])

    def get_settings(self) -> dict[str, Any]:
        return self.settings

    def get_template(self, template_id: str) -> str:
        return self.templates[template_id]

    def get_prompt(self, project_layout: ProjectLayout) -> Optional[str]:
        prompt_file = self.get_template("prompt")
        if prompt_file:
            prompt_path = project_layout.get_template_path(prompt_file)
            return safe_read_file(str(prompt_path))
        return None

    def with_name(self, name: str) -> "Profile":
        return Profile.create(name, self.gitignores, self.templates, self.settings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "gitignores": self.gitignores,
            "templates": self.templates,
            "settings": self.settings,
        }


@dataclass(frozen=True)
class SystemState:
    __warning__: str
    config_version: str
    default_profile: dict[str, Any]

    @staticmethod
    def create_new() -> "SystemState":
        return SystemState.create_default(str(CURRENT_CONFIG_VERSION))

    @staticmethod
    def create_null() -> "SystemState":
        return SystemState.create_default("0")

    @staticmethod
    def create_default(version: str) -> "SystemState":
        return SystemState.create(version, Profile.create_default().to_dict())

    @staticmethod
    def create(config_version: str, default_profile: dict[str, Any]) -> "SystemState":
        return SystemState(
            "This file is managed by llm-context. Manual edits will be overwritten.",
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
class Config:
    templates: dict[str, str]
    profiles: dict[str, dict[str, Any]]
    __info__: str = PROJECT_INFO

    @staticmethod
    def create_default() -> "Config":
        return Config(
            templates={
                "context": "lc-context.j2",
                "files": "lc-files.j2",
                "highlights": "lc-highlights.j2",
                "prompt": "lc-prompt.md",
            },
            profiles={
                "default": Profile.create_default().to_dict(),
                "code": Profile.create_code().to_dict(),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "__info__": self.__info__,
            "templates": self.templates,
            "profiles": self.profiles,
        }


@dataclass(frozen=True)
class ProfileResolver:
    config: dict[str, Any]

    @staticmethod
    def create(config: dict[str, Any]) -> "ProfileResolver":
        return ProfileResolver(config)

    def has_profile(self, profile_name: str) -> bool:
        return profile_name in self.config["profiles"]

    def get_profile(self, profile_name: str) -> Profile:
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
