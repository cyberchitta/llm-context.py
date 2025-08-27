import re
from dataclasses import dataclass
from logging import ERROR
from pathlib import Path
from typing import Any, Optional

import yaml

from llm_context.exceptions import RuleResolutionError
from llm_context.utils import ProjectLayout, Yaml, log

DEFAULT_CODE_RULE = "lc/prm-developer"


@dataclass(frozen=True)
class RuleParser:
    frontmatter: dict[str, Any]
    content: str
    path: Path

    @property
    def name(self) -> str:
        return self.path.stem

    @staticmethod
    def parse(content: str, path: Path) -> "RuleParser":
        frontmatter, markdown = RuleParser._extract_frontmatter(content)
        return RuleParser(frontmatter, markdown, path)

    @staticmethod
    def _extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)"
        match = re.search(frontmatter_pattern, content, re.DOTALL)
        if match:
            try:
                yaml_content = match.group(1)
                markdown_content = match.group(2)
                frontmatter = yaml.safe_load(yaml_content)
                return frontmatter or {}, markdown_content
            except yaml.YAMLError:
                return {}, content
        return {}, content

    def to_rule_config(self) -> dict[str, Any]:
        config = dict(self.frontmatter)
        config["name"] = self.name
        return config


@dataclass(frozen=True)
class RuleLoader:
    rules_dir: Path

    @staticmethod
    def create(project_layout: ProjectLayout) -> "RuleLoader":
        return RuleLoader(project_layout.rules_path)

    def _load_rule_from_path(self, path: Path) -> Optional[RuleParser]:
        if not path.exists():
            return None
        try:
            content = path.read_text()
            return RuleParser.parse(content, path)
        except Exception as e:
            log(ERROR, f"Failed to parse rule {path}: {str(e)}")
            return None

    def load_rule(self, name: str) -> RuleParser:
        path = self.rules_dir / f"{name}.md"
        if not path.exists():
            raise ValueError(
                f"Rule file '{name}.md' not found. Run 'lc-init' to restore default rules."
            )
        try:
            content = path.read_text()
            return RuleParser.parse(content, path)
        except Exception as e:
            raise RuleResolutionError(
                f"Failed to parse rule file '{name}.md': {str(e)}. This may indicate outdated rule syntax. "
                f"Consider updating the rule or switching to '{DEFAULT_CODE_RULE}' with: lc-set-rule {DEFAULT_CODE_RULE}"
            )

    def save_rule(self, name: str, frontmatter: dict[str, Any], content: str) -> Path:
        path = self.rules_dir / f"{name}.md"
        yaml_str = Yaml.dump(self._order_frontmatter(frontmatter))
        full_content = f"---\n{yaml_str}---\n{content}"
        path.write_text(full_content)
        return path

    def _order_frontmatter(self, frontmatter: dict[str, Any]) -> dict[str, Any]:
        field_groups = [
            ["name", "description", "instructions", "overview"],
            ["compose", "gitignores", "limit-to", "also-include"],
            ["implementations", "rules"],
        ]
        ordered_fields = [
            field for group in field_groups for field in group if field in frontmatter
        ]
        remaining_fields = [field for field in frontmatter if field not in ordered_fields]
        return {field: frontmatter[field] for field in ordered_fields + remaining_fields}


@dataclass(frozen=True)
class RuleProvider:
    rule_loader: "RuleLoader"

    @staticmethod
    def create(project_layout: ProjectLayout) -> "RuleProvider":
        return RuleProvider(RuleLoader.create(project_layout))

    def get_rule_content(self, rule_name: str) -> Optional[str]:
        rule = self.rule_loader.load_rule(rule_name)
        return rule.content if rule else None
