from dataclasses import dataclass
from importlib import resources
from logging import INFO
from pathlib import Path
from typing import Any

from llm_context import templates
from llm_context.profile import Profile, ProjectLayout, ToolConstants
from llm_context.utils import Toml, log

PROJECT_INFO: str = (
    "This project uses llm-context. For more information, visit: "
    "https://github.com/cyberchitta/llm-context.py or "
    "https://pypi.org/project/llm-context/"
)


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
class ProjectSetup:
    project_layout: ProjectLayout
    constants: ToolConstants

    @staticmethod
    def create(project_layout: ProjectLayout) -> "ProjectSetup":
        project_layout.templates_path.mkdir(parents=True, exist_ok=True)
        start_state = (
            ToolConstants.create_null()
            if not project_layout.state_path.exists()
            else ToolConstants(**Toml.load(project_layout.state_path))
        )
        return ProjectSetup(project_layout, start_state)

    def initialize(self):
        self._create_or_update_config_file()
        self._create_curr_ctx_file()
        self._update_templates_if_needed()
        self.create_state_file()

    def _create_or_update_config_file(self):
        if not self.project_layout.config_path.exists() or self.constants.needs_update:
            self._create_config_file()

    def _update_templates_if_needed(self):
        if self.constants.needs_update:
            config = Toml.load(self.project_layout.config_path)
            for _, template_name in config["templates"].items():
                template_path = self.project_layout.get_template_path(template_name)
                self._copy_template(template_name, template_path)

    def create_state_file(self):
        Toml.save(self.project_layout.state_path, ToolConstants.create_new().to_dict())

    def _create_config_file(self):
        Toml.save(self.project_layout.config_path, Config.create_default().to_dict())

    def _create_curr_ctx_file(self):
        if not self.project_layout.state_store_path.exists():
            Toml.save(self.project_layout.state_store_path, {"selections": {}})

    def _copy_template(self, template_name: str, dest_path: Path):
        template_content = resources.read_text(templates, template_name)
        dest_path.write_text(template_content)
        log(INFO, f"Updated template {template_name} to {dest_path}")
