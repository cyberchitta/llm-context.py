from dataclasses import dataclass
from importlib import resources
from logging import INFO
from pathlib import Path

from llm_context import templates
from llm_context.config import Config, Profile, ProjectLayout, SystemState
from llm_context.utils import Toml, log


@dataclass(frozen=True)
class ProjectSetup:
    project_layout: ProjectLayout
    state: SystemState

    @staticmethod
    def create(project_layout: ProjectLayout) -> "ProjectSetup":
        project_layout.templates_path.mkdir(parents=True, exist_ok=True)
        start_state = (
            SystemState.create_null()
            if not project_layout.state_path.exists()
            else SystemState(**Toml.load(project_layout.state_path))
        )
        return ProjectSetup(project_layout, start_state)

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
        log(INFO, f"Updated template {template_name} to {dest_path}")
