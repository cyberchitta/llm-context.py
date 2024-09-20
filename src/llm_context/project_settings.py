import json
import os
from dataclasses import dataclass
from importlib import resources
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
    "*.scm",
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
class ProjectLayout:
    root_path: Path

    @property
    def config_path(self) -> Path:
        return self.root_path / ".llm-context" / "config.toml"

    @property
    def context_storage_path(self) -> Path:
        return self.root_path / ".llm-context" / "curr_ctx.toml"

    @property
    def templates_path(self) -> Path:
        return self.root_path / ".llm-context" / "templates"

    def get_template_path(self, template_name: str) -> Path:
        return self.templates_path / template_name


@dataclass(frozen=True)
class SettingsInitializer:
    project_layout: ProjectLayout

    @staticmethod
    def create(project_layout: ProjectLayout) -> "SettingsInitializer":
        return SettingsInitializer(project_layout)

    def initialize(self):
        self._create_directory_structure()
        self._create_or_update_config_file()
        self._create_curr_ctx_file()
        self._copy_or_update_templates()

    def _create_directory_structure(self):
        self.project_layout.templates_path.mkdir(parents=True, exist_ok=True)

    def _create_or_update_config_file(self):
        config_path = self.project_layout.config_path
        if config_path.exists():
            self._update_config_file(config_path)
        else:
            self._create_config_file(config_path)

    def _create_config_file(self, config_path: Path):
        default_config = {
            "__info__": PROJECT_INFO,
            "config_version": "1",
            "templates": {
                "versions": {
                    "prompt": "1",
                    "context": "1",
                    "files": "1",
                    "highlights": "1",
                },
                "prompt": "lc-prompt.md",
                "context": "lc-context.j2",
                "files": "lc-files.j2",
                "highlights": "lc-highlights.j2",
            },
            "gitignores": {
                "full_files": GIT_IGNORE_DEFAULT,
                "outline_files": GIT_IGNORE_DEFAULT,
            },
            "summary_file": None,
        }
        ConfigLoader.save(config_path, default_config)

    def _update_config_file(self, config_path: Path):
        current_config = ConfigLoader.load(config_path)

        if version.parse(current_config.get("config_version", "0")) < version.parse("1"):
            # Perform any necessary migrations
            current_config["config_version"] = "1"
            # Add any new configuration options here
            ConfigLoader.save(config_path, current_config)

    def _copy_or_update_templates(self):
        config = ConfigLoader.load(self.project_layout.config_path)
        template_versions = (templates := config["templates"])["versions"]
        changes_made = False
        for template_key, current_version in template_versions.items():
            template_name = templates[template_key]
            template_path = self.project_layout.get_template_path(f"{template_name}")
            if not template_path.exists() or self._should_update_template(current_version):
                self._copy_template(template_name, template_path)
                template_versions[template_key] = "1"
                changes_made = True
        if changes_made:
            templates["versions"] = template_versions
            ConfigLoader.save(self.project_layout.config_path, config)

    def _should_update_template(self, current_version: str) -> bool:
        return current_version < "1"  # Compare with the current template version

    def _copy_template(self, template_name: str, dest_path: Path):
        template_content = resources.read_text(templates, f"{template_name}")
        dest_path.write_text(template_content)
        print(f"Updated template {template_name} to {dest_path}")

    def _create_curr_ctx_file(self):
        if not self.project_layout.context_storage_path.exists():
            ConfigLoader.save(self.project_layout.context_storage_path, {"context": {}})


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
class ContextStorage:
    storage_path: Path

    def get_stored_context(self) -> dict[str, list[str]]:
        context = ConfigLoader.load(self.storage_path).get("context", {})
        return cast(dict[str, list[str]], context)

    def store_context(self, context: dict[str, list[str]]):
        storage_data = ConfigLoader.load(self.storage_path)
        storage_data["context"] = context
        ConfigLoader.save(self.storage_path, storage_data)


@dataclass(frozen=True)
class ContextConfig:
    config: dict[str, Any]
    project_layout: ProjectLayout

    @staticmethod
    def create(project_layout: ProjectLayout) -> "ContextConfig":
        config = ConfigLoader.load(project_layout.config_path)
        return ContextConfig(config, project_layout)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        pattern = self.config.get("gitignores", {}).get(f"{context_type}_files", [])
        return cast(list[str], pattern)

    def get_prompt(self) -> Optional[str]:
        prompt_file = self.config["templates"]["prompt"]
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
class ProjectSettings:
    project_layout: ProjectLayout
    context_config: ContextConfig
    context_storage: ContextStorage

    @staticmethod
    def create(project_root: Path = Path.cwd()) -> "ProjectSettings":
        ProjectSettings.ensure_gitignore_exists(project_root)
        project_layout = ProjectLayout(project_root)
        initializer = SettingsInitializer.create(project_layout)
        initializer.initialize()
        context_config = ContextConfig.create(project_layout)
        context_storage = ContextStorage(project_layout.context_storage_path)
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
        return self.context_config.get_summary()

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


@LLMContextError.handle
def init_project():
    settings = ProjectSettings.create()
    print(f"LLM Context initialized for project: {settings.project_root}")
    print("You can now edit .llm-context/config.toml to customize ignore patterns.")
