from dataclasses import dataclass
from typing import Any, Optional, cast

from llm_context.utils import ProjectLayout, safe_read_file

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
