from dataclasses import dataclass
from importlib import resources
from logging import INFO
from pathlib import Path
from typing import Any

from llm_context import lc_resources
from llm_context.profile import Profile, ProjectLayout, ToolConstants
from llm_context.utils import Yaml, log

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
                "context-mcp": "lc-context-mcp.j2",
                "files": "lc-files.j2",
                "highlights": "lc-highlights.j2",
                "prompt": "lc-prompt.j2",
                "definitions": "lc-definitions.j2",
            },
            profiles={
                "code": Profile.create_code().to_dict(),
                "code-prompt": {
                    "base": "code",
                    "settings": {"with_prompt": True},
                    "description": "Extends 'code' by including LLM instructions from lc-prompt.md for guided interactions.",
                },
                "code-file": {
                    "base": "code",
                    "settings": {"context_file": "project-context.md.tmp"},
                    "description": "Extends 'code' by saving the generated context to 'project-context.md.tmp' for external use.",
                },
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
            else ToolConstants(**Yaml.load(project_layout.state_path))
        )
        return ProjectSetup(project_layout, start_state)

    def initialize(self):
        self._create_or_update_config_file()
        self._create_curr_ctx_file()
        self._update_templates_if_needed()
        self.create_state_file()
        self._create_or_update_ancillary_files()
        self._create_project_notes_file()
        self._create_user_notes_file()

    def _create_or_update_ancillary_files(self):
        if not self.project_layout.config_path.exists() or self.constants.needs_update:
            self._copy_template(
                "dotgitignore", self.project_layout.project_config_path / ".gitignore"
            )
            self._copy_template(
                "lc-prompt.md", self.project_layout.project_config_path / "lc-prompt.md"
            )

    def _create_or_update_config_file(self):
        if not self.project_layout.config_path.exists():
            self._create_config_file()
        elif self.constants.needs_update:
            self._update_config_file()

    def _create_curr_ctx_file(self):
        if not self.project_layout.state_store_path.exists():
            Yaml.save(self.project_layout.state_store_path, {"selections": {}})

    def _update_templates_if_needed(self):
        if self.constants.needs_update:
            config = Yaml.load(self.project_layout.config_path)
            for _, template_name in config["templates"].items():
                template_path = self.project_layout.get_template_path(template_name)
                self._copy_template(template_name, template_path)

    def create_state_file(self):
        Yaml.save(self.project_layout.state_path, ToolConstants.create_new().to_dict())

    def _create_project_notes_file(self):
        notes_path = self.project_layout.project_notes_path
        if not notes_path.exists():
            notes_path.write_text(
                "## Project Notes\n\n"
                "Add project-specific notes, documentation and guidelines here.\n"
                "This file is stored in the project repository.\n"
            )

    def _create_user_notes_file(self):
        notes_path = self.project_layout.user_notes_path
        if not notes_path.exists():
            notes_path.parent.mkdir(parents=True, exist_ok=True)
            notes_path.write_text(
                "## User Notes\n\n"
                "Add any personal notes or reminders about this or other projects here.\n"
                "This file is private and stored in your user config directory.\n"
            )

    def _update_config_file(self):
        user_config = Yaml.load(self.project_layout.config_path)
        new_config = Config.create_default().to_dict()
        new_profiles = new_config["profiles"]
        custom_profiles = {
            n: c for n, c in user_config.get("profiles", {}).items() if n not in new_profiles
        }
        merged_profiles = {**new_profiles, **custom_profiles}
        merged_config = {**new_config, "profiles": merged_profiles}
        Yaml.save(self.project_layout.config_path, merged_config)

    def _create_config_file(self):
        Yaml.save(self.project_layout.config_path, Config.create_default().to_dict())

    def _copy_template(self, template_name: str, dest_path: Path):
        template_content = resources.read_text(lc_resources, template_name)
        dest_path.write_text(template_content)
        log(INFO, f"Updated template {template_name} to {dest_path}")
