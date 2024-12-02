from dataclasses import dataclass
from importlib import resources
from logging import INFO
from pathlib import Path

from llm_context import templates
from llm_context.config import Config, Profile, ProfileResolver, ProjectLayout, SystemState
from llm_context.exceptions import LLMContextError
from llm_context.state import StateStore
from llm_context.utils import Toml, log


@dataclass(frozen=True)
class ProjectConfig:
    project_layout: ProjectLayout
    templates: dict[str, str]
    context_descriptor: Profile

    @staticmethod
    def create(project_root: Path, profile_name: str) -> "ProjectConfig":
        ProjectConfig.ensure_gitignore_exists(project_root)
        project_layout = ProjectLayout(project_root)
        SettingsInitializer.create(project_layout).initialize()
        raw_config = Toml.load(project_layout.config_path)
        profile = ProfileResolver.create(raw_config).get_profile(profile_name)
        return ProjectConfig(project_layout, raw_config["templates"], profile)

    @staticmethod
    def ensure_gitignore_exists(root_path: Path) -> None:
        if not (root_path / ".gitignore").exists():
            raise LLMContextError(
                "A .gitignore file is essential for this tool to function correctly. Please create one before proceeding.",
                "GITIGNORE_NOT_FOUND",
            )

    def has_profile(self, profile_name: str):
        raw_config = Toml.load(self.project_layout.config_path)
        return ProfileResolver.create(raw_config).has_profile(profile_name)

    @property
    def state_store(self):
        return StateStore(self.project_layout.state_store_path)

    @property
    def project_root_path(self):
        return self.project_layout.root_path

    @property
    def project_root(self):
        return str(self.project_root_path)


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
        log(INFO, f"Updated template {template_name} to {dest_path}")
