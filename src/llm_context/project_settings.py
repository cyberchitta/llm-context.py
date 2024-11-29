import argparse
from dataclasses import dataclass
from importlib import resources
from importlib.metadata import version as pkg_ver
from pathlib import Path
from typing import Any, Optional, cast

import toml
from packaging import version

from llm_context import templates
from llm_context.exceptions import LLMContextError
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
    def context_storage_path(self) -> Path:
        return self.root_path / ".llm-context" / "curr_ctx.toml"

    @property
    def templates_path(self) -> Path:
        return self.root_path / ".llm-context" / "templates"

    def get_template_path(self, template_name: str) -> Path:
        return self.templates_path / template_name


@dataclass(frozen=True)
class ConfigLoader:
    @staticmethod
    def load(file_path: Path) -> dict[str, Any]:
        with open(file_path, "r") as f:
            return toml.load(f)

    @staticmethod
    def save(file_path: Path, data: dict[str, Any]):
        with open(file_path, "w") as f:
            toml.dump(data, f)


@dataclass(frozen=True)
class ProfileTemplate:
    @staticmethod
    def create_default_gitignores() -> list[str]:
        return GIT_IGNORE_DEFAULT

    @staticmethod
    def create_default() -> dict[str, Any]:
        return {
            "gitignores": {
                "full_files": ProfileTemplate.create_default_gitignores(),
                "outline_files": ProfileTemplate.create_default_gitignores(),
            },
            "templates": {
                "prompt": "lc-prompt.md",
            },
            "settings": {
                "with_prompt": False,
                "no_media": False,
            },
        }

    @staticmethod
    def create_code() -> dict[str, Any]:
        return ProfileTemplate.create_default()


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
        return SystemState.create(version, ProfileTemplate.create_default())

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
    summary_file: Optional[str]
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
                "default": ProfileTemplate.create_default(),
                "code": ProfileTemplate.create_code(),
            },
            summary_file=None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "__info__": self.__info__,
            "templates": self.templates,
            "profiles": self.profiles,
            "summary_file": self.summary_file,
        }


@dataclass(frozen=True)
class ContextStorage:
    storage_path: Path

    def load(self) -> dict[str, Any]:
        return ConfigLoader.load(self.storage_path)

    def get_profile(self) -> str:
        return cast(str, self.load().get("profile", "code"))

    def store_profile(self, profile: str):
        storage_data = ConfigLoader.load(self.storage_path)
        storage_data["profile"] = profile
        ConfigLoader.save(self.storage_path, storage_data)

    def get_stored_context(self) -> dict[str, list[str]]:
        context = self.load().get("context", {})
        return cast(dict[str, list[str]], context)

    def store_context(self, context: dict[str, list[str]]):
        storage_data = ConfigLoader.load(self.storage_path)
        storage_data["context"] = context
        ConfigLoader.save(self.storage_path, storage_data)


@dataclass(frozen=True)
class ContextConfig:
    config: dict[str, Any]
    project_layout: ProjectLayout
    profile: str

    @staticmethod
    def _resolve_profile(config: dict[str, Any], profile_name: str) -> dict[str, Any]:
        try:
            profile_config = config["profiles"][profile_name]
        except KeyError:
            raise ValueError(f"Profile '{profile_name}' not found in config")
        if "base" not in profile_config:
            return profile_config
        base_name = profile_config["base"]
        try:
            base_profile = ContextConfig._resolve_profile(config, base_name)
        except KeyError:
            raise ValueError(
                f"Base profile '{base_name}' referenced by '{profile_name}' not found in config",
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

    @staticmethod
    def create(project_layout: ProjectLayout, profile: str) -> "ContextConfig":
        raw_config = ConfigLoader.load(project_layout.config_path)
        resolved_config = raw_config.copy()
        resolved_config["profiles"][profile] = ContextConfig._resolve_profile(raw_config, profile)
        return ContextConfig(resolved_config, project_layout, profile)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        pattern = (
            self.config["profiles"][self.profile]
            .get("gitignores", {})
            .get(f"{context_type}_files", [])
        )
        return cast(list[str], pattern)

    def get_settings(self) -> dict[str, Any]:
        return cast(dict[str, Any], self.config["profiles"][self.profile]["settings"])

    def get_prompt(self) -> Optional[str]:
        prompt_file = self.config["profiles"][self.profile]["templates"]["prompt"]
        if prompt_file:
            prompt_path = self.project_layout.get_template_path(prompt_file)
            return safe_read_file(str(prompt_path))
        return None

    def get_summary(self) -> Optional[str]:
        summary_file = self.config.get("summary_file")
        if summary_file:
            summary_path = self.project_layout.root_path / summary_file
            return safe_read_file(str(summary_path))
        return None


@dataclass(frozen=True)
class SettingsInitializer:
    project_layout: ProjectLayout
    state: SystemState

    @staticmethod
    def create(project_layout: ProjectLayout) -> "SettingsInitializer":
        project_layout.templates_path.mkdir(parents=True, exist_ok=True)
        start_state = (
            SystemState.create_null()
            if not project_layout.state_path.exists()
            else SystemState(**ConfigLoader.load(project_layout.state_path))
        )
        return SettingsInitializer(project_layout, start_state)

    def initialize(self):
        self._create_or_update_config_file()
        self._create_curr_ctx_file()
        self._update_templates_if_needed()
        self.create_state_file()

    def _create_or_update_config_file(self):
        if not self.project_layout.config_path.exists() or self.state.needs_update:
            self._create_config_file()

    def _update_templates_if_needed(self):
        if self.state.needs_update:
            config = ConfigLoader.load(self.project_layout.config_path)
            for _, template_name in config["templates"].items():
                template_path = self.project_layout.get_template_path(template_name)
                self._copy_template(template_name, template_path)

    def create_state_file(self):
        ConfigLoader.save(self.project_layout.state_path, SystemState.create_new().to_dict())

    def _create_config_file(self):
        ConfigLoader.save(self.project_layout.config_path, Config.create_default().to_dict())

    def _create_curr_ctx_file(self):
        if not self.project_layout.context_storage_path.exists():
            ConfigLoader.save(
                self.project_layout.context_storage_path, {"profile": "code", "context": {}}
            )

    def _copy_template(self, template_name: str, dest_path: Path):
        template_content = resources.read_text(templates, template_name)
        dest_path.write_text(template_content)
        print(f"Updated template {template_name} to {dest_path}")


@dataclass(frozen=True)
class ProjectSettings:
    project_layout: ProjectLayout
    context_config: ContextConfig
    context_storage: ContextStorage

    @staticmethod
    def create(project_root: Path = Path.cwd()) -> "ProjectSettings":
        ProjectSettings.ensure_gitignore_exists(project_root)
        project_layout = ProjectLayout(project_root)
        SettingsInitializer.create(project_layout).initialize()
        context_storage = ContextStorage(project_layout.context_storage_path)
        profile = context_storage.get_profile()
        context_config = ContextConfig.create(project_layout, profile)
        return ProjectSettings(project_layout, context_config, context_storage)

    @staticmethod
    def ensure_gitignore_exists(root_path: Path) -> None:
        if not (root_path / ".gitignore").exists():
            raise LLMContextError(
                "A .gitignore file is essential for this tool to function correctly. Please create one before proceeding.",
                "GITIGNORE_NOT_FOUND",
            )

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.context_config.get_ignore_patterns(context_type)

    def get_summary(self) -> Optional[str]:
        return cast(Optional[str], self.context_config.get_summary())

    def get_prompt(self) -> Optional[str]:
        return self.context_config.get_prompt()

    def get_stored_context(self) -> dict[str, list[str]]:
        return self.context_storage.get_stored_context()

    def store_context(self, context: dict[str, list[str]]):
        self.context_storage.store_context(context)

    def get_template_path(self, template_name: str) -> Path:
        return self.project_layout.get_template_path(template_name)

    def file_list(self, content_type: str, in_files: list[str] = []) -> list[str]:
        files = self.context_storage.get_stored_context()[content_type]
        return files if not in_files else in_files

    @property
    def project_root_path(self):
        return self.project_layout.root_path

    @property
    def project_root(self):
        return str(self.project_root_path)


def profile_feedback():
    profile = ProjectSettings.create().context_storage.get_profile()
    print(f"Active profile: {profile}")


@LLMContextError.handle
def init_project():
    settings = ProjectSettings.create()
    print(f"LLM Context initialized for project: {settings.project_root}")
    print("You can now edit .llm-context/config.toml to customize ignore patterns.")


def set_profile(profile: str):
    settings = ProjectSettings.create()
    if profile not in settings.context_config.config["profiles"]:
        raise ValueError(f"Profile '{profile}' does not exist.")
    settings.context_storage.store_profile(profile)
    print(f"Active profile set to '{profile}'.")


@LLMContextError.handle
def set_profile_with_args():
    parser = argparse.ArgumentParser(description="Set active profile for LLM context")
    parser.add_argument(
        "profile",
        type=str,
        help="Profile to set as active",
    )
    args = parser.parse_args()
    set_profile(args.profile)


@LLMContextError.handle
def show_version():
    print(f"llm-context version {pkg_ver('llm-context')}")
