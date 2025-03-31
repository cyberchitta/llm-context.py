import re
from dataclasses import dataclass
from logging import ERROR
from pathlib import Path
from typing import Any, Optional

import yaml

from llm_context.utils import ProjectLayout, log


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

    def load_all_rules(self) -> dict[str, RuleParser]:
        return {
            rule.name: rule
            for path in self.rules_dir.glob("*.md")
            if (rule := self._load_rule_from_path(path)) is not None
        }

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
            raise ValueError(
                f"Failed to parse rule file '{name}.md': {str(e)}. Run 'lc-init' to restore default rules."
            )

    def save_rule(self, name: str, frontmatter: dict[str, Any], content: str) -> Path:
        path = self.rules_dir / f"{name}.md"
        yaml_str = yaml.dump(frontmatter, default_flow_style=False)
        full_content = f"---\n{yaml_str}---\n\n{content}"
        path.write_text(full_content)
        return path


@dataclass(frozen=True)
class RuleProvider:
    rule_loader: "RuleLoader"

    @staticmethod
    def create(project_layout: ProjectLayout) -> "RuleProvider":
        return RuleProvider(RuleLoader.create(project_layout))

    def get_rule_content(self, rule_name: str) -> Optional[str]:
        rule = self.rule_loader.load_rule(rule_name)
        return rule.content if rule else None
