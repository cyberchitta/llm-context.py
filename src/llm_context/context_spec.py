from dataclasses import dataclass
from pathlib import Path

from llm_context.exceptions import LLMContextError
from llm_context.project_setup import ProjectSetup
from llm_context.rule import Rule, RuleResolver, ToolConstants
from llm_context.state import StateStore
from llm_context.utils import ProjectLayout, Yaml


@dataclass(frozen=True)
class ContextSpec:
    project_layout: ProjectLayout
    templates: dict[str, str]
    rule: Rule
    state: ToolConstants

    @staticmethod
    def create(project_root: Path, rule_name: str, state: ToolConstants) -> "ContextSpec":
        ContextSpec.ensure_gitignore_exists(project_root)
        project_layout = ProjectLayout(project_root)
        ProjectSetup.create(project_layout).initialize()
        raw_config = Yaml.load(project_layout.config_path)
        resolver = RuleResolver.create(state, project_layout)
        rule = resolver.get_rule(rule_name)
        return ContextSpec(project_layout, raw_config["templates"], rule, state)

    @staticmethod
    def ensure_gitignore_exists(root_path: Path) -> None:
        if not (root_path / ".gitignore").exists():
            raise LLMContextError(
                "A .gitignore file is essential for this tool to function correctly. Please create one before proceeding.",
                "GITIGNORE_NOT_FOUND",
            )

    def has_rule(self, rule_name: str):
        resolver = RuleResolver.create(self.state, self.project_layout)
        return resolver.has_rule(rule_name)

    @property
    def state_store(self):
        return StateStore(self.project_layout.state_store_path)

    @property
    def project_root_path(self):
        return self.project_layout.root_path

    @property
    def project_root(self):
        return str(self.project_root_path)
