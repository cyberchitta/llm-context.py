from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from packaging import version

from llm_context.utils import ProjectLayout, Yaml, safe_read_file

CURRENT_CONFIG_VERSION = version.parse("2.8")

MEDIA_EXTENSIONS: set[str] = {
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
}

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
class Profile:
    gitignores: dict[str, list[str]]
    only_includes: dict[str, list[str]]
    prompt: str
    description: str

    @staticmethod
    def create_code_gitignores() -> "Profile":
        media = [f"*.{ext.lstrip('.')}" for ext in MEDIA_EXTENSIONS]
        return Profile.create(
            {
                "full_files": GITIGNORE,
                "outline_files": GITIGNORE,
                "diagram_files": media,
            },
            {"full_files": INCLUDE_ALL, "outline_files": INCLUDE_ALL, "diagram_files": INCLUDE_ALL},
            "",
            "Base ignore patterns for code files, customize this for project-specific ignores.",
        )

    @staticmethod
    def create_code_dict() -> dict[str, Any]:
        """Creates the default code profile configuration."""
        return {
            "base": DEFAULT_GITIGNORES_PROFILE,
            "prompt": "lc-prompt.md",
            "description": f"Default profile for software projects, using {DEFAULT_GITIGNORES_PROFILE} base profile.",
        }

    @staticmethod
    def from_config(config: dict[str, Any]) -> "Profile":
        return Profile.create(
            config["gitignores"],
            config["only-include"],
            config.get("prompt", ""),
            config.get("description", ""),
        )

    @staticmethod
    def create(gitignores, only_include, prompt, description) -> "Profile":
        return Profile(gitignores, only_include, prompt, description)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.gitignores.get(f"{context_type}_files", IGNORE_NOTHING)

    def get_only_includes(self, context_type: str) -> list[str]:
        return self.only_includes.get(f"{context_type}_files", INCLUDE_ALL)

    def get_prompt(self, project_layout: ProjectLayout) -> Optional[str]:
        if not self.prompt:
            return None
        prompt_path = project_layout.project_config_path / self.prompt
        return safe_read_file(str(prompt_path))

    def get_project_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.project_notes_path))

    def get_user_notes(self, project_layout: ProjectLayout) -> Optional[str]:
        return safe_read_file(str(project_layout.user_notes_path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "gitignores": self.gitignores,
            "only-include": self.only_includes,
            "prompt": self.prompt,
            "description": self.description,
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
        return ToolConstants.create(version, Profile.create_code_dict())

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
            return Profile.from_config(self.system_state.default_profile)
        resolved_config = self.resolve_profile(profile_name)
        return Profile.from_config(resolved_config)

    def resolve_profile(self, profile_name: str) -> dict[str, Any]:
        if profile_name == "default":
            return self.system_state.default_profile
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
