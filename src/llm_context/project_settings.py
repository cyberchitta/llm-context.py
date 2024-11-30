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
    def state_store_path(self) -> Path:
        return self.root_path / ".llm-context" / "curr_ctx.toml"

    @property
    def templates_path(self) -> Path:
        return self.root_path / ".llm-context" / "templates"

    def get_template_path(self, template_name: str) -> Path:
        return self.templates_path / template_name


@dataclass(frozen=True)
class Toml:
    @staticmethod
    def load(file_path: Path) -> dict[str, Any]:
        with open(file_path, "r") as f:
            return toml.load(f)

    @staticmethod
    def save(file_path: Path, data: dict[str, Any]):
        with open(file_path, "w") as f:
            toml.dump(data, f)


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
    def create(name, gitignores, templates, settings):
        return Profile(name, gitignores, templates, settings)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.gitignores.get(f"{context_type}_files", [])

    def get_settings(self) -> dict[str, Any]:
        return self.settings

    def get_template(self, template_id: str) -> str:
        return self.templates[template_id]

    def get_prompt(self) -> Optional[str]:
        prompt_file = self.get_template("prompt")
        if prompt_file:
            prompt_path = self.project_layout.get_template_path(prompt_file)
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
class FileSelection:
    profile: str
    full_files: list[str]
    outline_files: list[str]

    @staticmethod
    def create_default():
        return FileSelection.create("code", None, None)

    @staticmethod
    def create(profile: str, full_files: list[str], outline_files: list[str]):
        return FileSelection(profile, full_files, outline_files)

    def with_profile(self, profile: str):
        FileSelection.create(profile, self.full_files, self.outline_files)


@dataclass(frozen=True)
class StateStore:
    storage_path: Path

    def load(self) -> FileSelection:
        data = Toml.load(self.storage_path)
        return FileSelection.create(
            data.get("profile", "code"),
            data.get("file_lists", {}).get("full", []),
            data.get("file_lists", {}).get("outline", []),
        )

    def save(self, state: FileSelection):
        data = {
            "profile": state.profile,
            "file_lists": {"full": state.full_files, "outline": state.outline_files},
        }
        Toml.save(self.storage_path, data)


@dataclass(frozen=True)
class ProfileResolver:
    config: dict[str, Any]

    @staticmethod
    def create(config: dict[str, Any]) -> "ProfileResolver":
        return ProfileResolver(config)

    def get_profile(self, profile_name: str) -> Profile:
        resolved_config = self.resolve_profile(profile_name)
        return Profile.from_config(profile_name, resolved_config)

    def resolve_profile(self, profile_name: str) -> dict[str, Any]:
        try:
            profile_config = self.config["profiles"][profile_name]
        except KeyError:
            raise ValueError(f"Profile '{profile_name}' not found in config")
        if "base" not in profile_config:
            return profile_config
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
            else SystemState(**Toml.load(project_layout.state_path))
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
            config = Toml.load(self.project_layout.config_path)
            for _, template_name in config["templates"].items():
                template_path = self.project_layout.get_template_path(template_name)
                self._copy_template(template_name, template_path)

    def create_state_file(self):
        Toml.save(self.project_layout.state_path, SystemState.create_new().to_dict())

    def _create_config_file(self):
        Toml.save(self.project_layout.config_path, Config.create_default().to_dict())

    def _create_curr_ctx_file(self):
        if not self.project_layout.state_store_path.exists():
            Toml.save(self.project_layout.state_store_path, Profile.create_default().to_dict())

    def _copy_template(self, template_name: str, dest_path: Path):
        template_content = resources.read_text(templates, template_name)
        dest_path.write_text(template_content)
        print(f"Updated template {template_name} to {dest_path}")


@dataclass(frozen=True)
class ProjectSettings:
    project_layout: ProjectLayout
    templates: dict[str, str]
    filter_descriptor: Profile
    file_selection: FileSelection

    @staticmethod
    def create(project_root: Path) -> "ProjectSettings":
        ProjectSettings.ensure_gitignore_exists(project_root)
        project_layout = ProjectLayout(project_root)
        SettingsInitializer.create(project_layout).initialize()
        file_selection = StateStore(project_layout.state_store_path).load()
        profile_name = file_selection.profile
        raw_config = Toml.load(project_layout.config_path)
        templates = raw_config["templates"]
        resolver = ProfileResolver.create(raw_config)
        filter_descriptor = resolver.get_profile(profile_name)
        return ProjectSettings(project_layout, templates, filter_descriptor, file_selection)

    @staticmethod
    def ensure_gitignore_exists(root_path: Path) -> None:
        if not (root_path / ".gitignore").exists():
            raise LLMContextError(
                "A .gitignore file is essential for this tool to function correctly. Please create one before proceeding.",
                "GITIGNORE_NOT_FOUND",
            )

    @property
    def state_store(self):
        return StateStore(self.project_layout.state_store_path)

    @property
    def project_root_path(self):
        return self.project_layout.root_path

    @property
    def project_root(self):
        return str(self.project_root_path)


def profile_feedback(project_root: Path):
    profile = ProjectSettings.create(project_root).file_selection.profile
    print(f"Active profile: {profile}")


@LLMContextError.handle
def init_project():
    settings = ProjectSettings.create(Path.cwd())
    print(f"LLM Context initialized for project: {settings.project_root}")
    print("You can now edit .llm-context/config.toml to customize ignore patterns.")


def set_profile(profile: str):
    settings = ProjectSettings.create(Path.cwd())
    if profile not in settings.filter_descriptor.config["profiles"]:
        raise ValueError(f"Profile '{profile}' does not exist.")
    file_selection = settings.file_selection.with_profile(profile)
    settings.state_store.save(file_selection)
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
