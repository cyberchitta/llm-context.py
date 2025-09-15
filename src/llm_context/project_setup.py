import shutil
from dataclasses import dataclass
from importlib import resources
from logging import INFO
from pathlib import Path
from typing import Any

from llm_context import lc_resources
from llm_context.lc_resources import rules, templates
from llm_context.rule import ProjectLayout, ToolConstants
from llm_context.state import StateStore
from llm_context.utils import Yaml, log

PROJECT_INFO: str = (
    "This project uses llm-context. For more information, visit: "
    "https://github.com/cyberchitta/llm-context.py or "
    "https://pypi.org/project/llm-context/"
)

SYSTEM_RULES = [
    "lc/exc-base.md",
    "lc/flt-base.md",
    "lc/flt-no-files.md",
    "lc/flt-no-full.md",
    "lc/flt-no-outline.md",
    "lc/ins-developer.md",
    "lc/ins-rule-framework.md",
    "lc/ins-rule-intro.md",
    "lc/prm-developer.md",
    "lc/prm-rule-create.md",
    "lc/sty-code.md",
    "lc/sty-javascript.md",
    "lc/sty-jupyter.md",
    "lc/sty-python.md",
]


@dataclass(frozen=True)
class Config:
    templates: dict[str, str]
    __info__: str = PROJECT_INFO

    @staticmethod
    def create_default() -> "Config":
        return Config(
            templates={
                "context": "lc/context.j2",
                "definitions": "lc/definitions.j2",
                "end-prompt": "lc/end-prompt.j2",
                "excerpts": "lc/excerpts.j2",
                "excluded": "lc/excluded.j2",
                "files": "lc/files.j2",
                "missing-files": "lc/missing-files.j2",
                "outlines": "lc/outlines.j2",
                "overview": "lc/overview.j2",
                "prompt": "lc/prompt.j2",
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "__info__": self.__info__,
            "templates": self.templates,
        }


@dataclass(frozen=True)
class ProjectSetup:
    project_layout: ProjectLayout
    constants: ToolConstants

    @staticmethod
    def create(project_layout: ProjectLayout) -> "ProjectSetup":
        project_layout.templates_path.mkdir(parents=True, exist_ok=True)
        project_layout.rules_path.mkdir(parents=True, exist_ok=True)
        StateStore.delete_if_stale_rule(project_layout)
        start_state = (
            ToolConstants.create_null()
            if not project_layout.state_path.exists()
            else ToolConstants.from_dict(Yaml.load(project_layout.state_path))
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
        self._setup_default_rules()

    def _create_or_update_ancillary_files(self):
        if not self.project_layout.config_path.exists() or self.constants.needs_update:
            self._copy_resource(
                "dotgitignore", self.project_layout.project_config_path / ".gitignore"
            )

    def _create_or_update_config_file(self):
        if not self.project_layout.config_path.exists():
            self._create_config_file()
        elif self.constants.needs_update:
            self._update_config_file()
            self._clean_old_resources()

    def _create_curr_ctx_file(self):
        if not self.project_layout.state_store_path.exists():
            Yaml.save(self.project_layout.state_store_path, {"selections": {}})

    def _update_templates_if_needed(self):
        if self.constants.needs_update:
            config = Yaml.load(self.project_layout.config_path)
            for _, template_name in config["templates"].items():
                template_path = self.project_layout.get_template_path(template_name)
                self._copy_template(template_name, template_path)
            self._copy_excerpter_templates()

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
                "Add Any personal notes or reminders about this or other projects here.\n"
                "This file is private and stored in your user config directory.\n"
            )

    def _update_config_file(self):
        new_config = Config.create_default().to_dict()
        Yaml.save(self.project_layout.config_path, new_config)

    def _create_config_file(self):
        Yaml.save(self.project_layout.config_path, Config.create_default().to_dict())

    def _copy_resource(self, resource_name: str, dest_path: Path):
        template_content = resources.files(lc_resources).joinpath(resource_name).read_text()
        dest_path.write_text(template_content)
        log(INFO, f"Updated resource {resource_name} to {dest_path}")

    def _copy_template(self, template_name: str, dest_path: Path):
        template_content = resources.files(templates).joinpath(template_name).read_text()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(template_content)
        log(INFO, f"Updated template {template_name} to {dest_path}")

    def _copy_rule(self, rule_file: str, dest_path: Path):
        rules_path = resources.files(rules)
        rule_path = rules_path / rule_file
        rule_content = rule_path.read_text()
        dest_path.write_text(rule_content)
        log(INFO, f"Updated rule {rule_file} to {dest_path}")

    def _setup_default_rules(self):
        lc_rules_path = self.project_layout.rules_path / "lc"
        if not self.constants.needs_update and lc_rules_path.exists():
            return
        if lc_rules_path.exists():
            shutil.rmtree(lc_rules_path)
            log(INFO, "Refreshing system rules")
        lc_rules_path.mkdir(parents=True, exist_ok=True)
        for rule in SYSTEM_RULES:
            rule_path = self.project_layout.get_rule_path(rule)
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            self._copy_rule(rule, rule_path)

    def _copy_excerpter_templates(self):
        excerpters_source = resources.files(templates).joinpath("lc").joinpath("excerpters")
        excerpters_dest = self.project_layout.templates_path / "lc" / "excerpters"
        if excerpters_source.is_dir():
            excerpters_dest.mkdir(parents=True, exist_ok=True)
            for template_file in excerpters_source.iterdir():
                if template_file.is_file() and template_file.name.endswith(".j2"):
                    dest_file = excerpters_dest / template_file.name
                    dest_file.write_text(template_file.read_text())
                    log(INFO, f"Updated excerpter template {template_file.name} to {dest_file}")

    def _clean_old_resources(self):
        templates_path = self.project_layout.templates_path
        if templates_path.exists():
            for template_file in templates_path.rglob("lc-*.j2"):
                template_file.unlink()
                log(INFO, f"Removed old template {template_file}")
        rules_path = self.project_layout.rules_path
        if rules_path.exists():
            for rule_file in rules_path.rglob("lc-*.md"):
                rule_file.unlink()
                log(INFO, f"Removed old rule {rule_file}")
