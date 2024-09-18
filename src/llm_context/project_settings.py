import json
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Optional

from llm_context import templates

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


@dataclass(frozen=True)
class ProjectLayout:
    root_path: Path

    @property
    def config_path(self) -> Path:
        return self.root_path / ".llm-context" / "config.json"

    @property
    def context_storage_path(self) -> Path:
        return self.root_path / ".llm-context" / "curr_ctx.json"

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
        self._create_config_file()
        self._create_curr_ctx_file()
        self._copy_default_templates()

    def _create_directory_structure(self):
        self.project_layout.templates_path.mkdir(parents=True, exist_ok=True)

    def _create_config_file(self):
        if not self.project_layout.config_path.exists():
            default_config = {
                "__info__": PROJECT_INFO,
                "gitignores": {
                    "full_files": GIT_IGNORE_DEFAULT,
                    "outline_files": GIT_IGNORE_DEFAULT,
                },
                "summary_file": None,
                "templates": {
                    "context": "context.j2",
                    "files": "files.j2",
                    "highlights": "highlights.j2",
                },
            }
            ConfigLoader.save(self.project_layout.config_path, default_config)

    def _create_curr_ctx_file(self):
        if not self.project_layout.context_storage_path.exists():
            ConfigLoader.save(self.project_layout.context_storage_path, {"context": {}})

    def _copy_default_templates(self):
        if not self.project_layout.templates_path.exists():
            self.project_layout.templates_path.mkdir(parents=True, exist_ok=True)
            template_files = [r for r in resources.contents(templates) if r.endswith(".j2")]
            for template_file in template_files:
                template_content = resources.read_text(templates, template_file)
                dest_file = self.project_layout.get_template_path(template_file)
                dest_file.write_text(template_content)
                print(f"Copied template {template_file} to {dest_file}")


@dataclass(frozen=True)
class ConfigLoader:
    @staticmethod
    def load(file_path: Path) -> dict[str, Any]:
        with open(file_path, "r") as f:
            return json.load(f)

    @staticmethod
    def save(file_path: Path, data: dict[str, Any]):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)


@dataclass(frozen=True)
class ContextStorage:
    storage_path: Path

    def get_stored_context(self) -> dict[str, list[str]]:
        return ConfigLoader.load(self.storage_path).get("context", {})

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
        gi = self.config.get("gitignores", {})
        return gi.get(f"{context_type}_files", [])

    def get_summary(self) -> Optional[str]:
        summary_file = self.config.get("summary_file")
        if summary_file:
            summary_path = self.project_layout.root_path / summary_file
            return summary_path.read_text() if summary_path.exists() else None
        return None


@dataclass(frozen=True)
class ProjectSettings:
    project_layout: ProjectLayout
    context_config: ContextConfig
    context_storage: ContextStorage

    @staticmethod
    def create(project_root: Path = Path.cwd()) -> "ProjectSettings":
        project_layout = ProjectLayout(project_root)
        initializer = SettingsInitializer.create(project_layout)
        initializer.initialize()
        context_config = ContextConfig.create(project_layout)
        context_storage = ContextStorage(project_layout.context_storage_path)
        return ProjectSettings(project_layout, context_config, context_storage)

    def get_ignore_patterns(self, context_type: str) -> list[str]:
        return self.context_config.get_ignore_patterns(context_type)

    def get_summary(self) -> Optional[str]:
        return self.context_config.get_summary()

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
