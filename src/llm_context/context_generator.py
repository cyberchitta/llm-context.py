import random
from dataclasses import dataclass
from datetime import datetime
from logging import ERROR
from pathlib import Path
from typing import Any, Optional, cast

from jinja2 import Environment, FileSystemLoader  # type: ignore

from llm_context.context_spec import ContextSpec
from llm_context.excerpters.base import Excerpts
from llm_context.excerpters.language_mapping import to_language
from llm_context.excerpters.parser import Source
from llm_context.excerpters.service import ExcerpterRegistry
from llm_context.file_selector import FileSelector
from llm_context.overviews import get_focused_overview, get_full_overview
from llm_context.rule import IGNORE_NOTHING, INCLUDE_ALL, Rule
from llm_context.rule_parser import RuleLoader, RuleProvider
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, ProjectLayout, safe_read_file


@dataclass(frozen=True)
class Template:
    name: str
    context: dict
    env: Environment

    @staticmethod
    def create(name: str, context: dict, templates_path) -> "Template":
        env = Environment(loader=FileSystemLoader(str(templates_path)))
        return Template(name, context, env)

    def render(self) -> str:
        template = self.env.get_template(self.name)
        return template.render(**self.context)


@dataclass(frozen=True)
class ContextCollector:
    root_path: Path
    converter: PathConverter
    project_layout: ProjectLayout
    rule_loader: RuleLoader

    @staticmethod
    def get_excerpter() -> ExcerpterRegistry:
        return ExcerpterRegistry.create()

    @staticmethod
    def create(root_path: Path) -> "ContextCollector":
        project_layout = ProjectLayout(root_path)
        rule_loader = RuleLoader.create(project_layout)
        return ContextCollector(
            root_path, PathConverter.create(root_path), project_layout, rule_loader
        )

    def sample_file_abs(self, full_abs: list[str]) -> list[str]:
        all_abs = set(
            FileSelector.create(self.root_path, IGNORE_NOTHING, INCLUDE_ALL, []).get_files()
        )
        incomplete_files = sorted(list(all_abs - set(full_abs)))
        return random.sample(incomplete_files, min(2, len(incomplete_files)))

    def files(self, rel_paths: list[str]) -> list[dict[str, str]]:
        abs_paths = self.converter.to_absolute(rel_paths)
        return [
            {"path": rel_path, "content": content}
            for rel_path, abs_path in zip(rel_paths, abs_paths)
            if (content := safe_read_file(abs_path)) is not None
        ]

    def excerpts(self, tagger: Any, rel_paths: list[str], rule: Rule) -> Excerpts:
        abs_paths = self.converter.to_absolute(rel_paths)
        excerpter = self.get_excerpter()
        if rel_paths:
            sources = [
                Source(rel, content)
                for rel, abs_path in zip(rel_paths, abs_paths)
                if (content := safe_read_file(abs_path)) is not None
            ]
            return excerpter.excerpt(sources, rule, tagger)[0]
        else:
            return excerpter.empty()

    def definitions(self, tagger: Any, requests: list[tuple[str, str]]) -> list[dict[str, Any]]:
        if requests and ContextCollector.get_excerpter():
            from llm_context.excerpters.parser import Source
            from llm_context.excerpters.tagger import find_definition

            rel_paths = list({path for path, _ in requests})
            abs_paths = self.converter.to_absolute(rel_paths)
            sources = [
                Source(rel, content)
                for rel, abs_path in zip(rel_paths, abs_paths)
                if (content := safe_read_file(abs_path)) is not None
            ]
            all_defs = {source.rel_path: tagger.extract_definitions(source) for source in sources}
            return [
                {"path": path, "name": name, "code": find_definition(all_defs.get(path, []), name)}
                for path, name in requests
            ]
        else:
            return []

    def overview(
        self,
        overview_mode: str,
        full_abs: list[str],
        excerpted_abs: list[str],
        rule_abs: list[str],
        diagram_ignores: list[str],
    ) -> str:
        return (
            get_full_overview(self.root_path, full_abs, excerpted_abs, rule_abs, diagram_ignores)
            if overview_mode == "full"
            else get_focused_overview(
                self.root_path, full_abs, excerpted_abs, rule_abs, diagram_ignores
            )
        )


@dataclass(frozen=True)
class ContextSettings:
    with_prompt: bool = False
    with_user_notes: bool = False
    tools_available: bool = True

    @staticmethod
    def create(
        with_prompt: bool, with_user_notes: bool, tools_available: bool
    ) -> "ContextSettings":
        return ContextSettings(with_prompt, with_user_notes, tools_available)


@dataclass(frozen=True)
class ContextGenerator:
    collector: ContextCollector
    spec: ContextSpec
    project_root: Path
    converter: PathConverter
    full_rel: list[str]
    full_abs: list[str]
    excerpted_rel: list[str]
    excerpted_abs: list[str]
    settings: ContextSettings
    tagger: Optional[Any]

    @staticmethod
    def create(
        spec: ContextSpec,
        file_selection: FileSelection,
        settings: ContextSettings,
        tagger: Optional[Any] = None,
    ) -> "ContextGenerator":
        project_root = spec.project_root_path
        collector = ContextCollector.create(project_root)
        converter = PathConverter.create(project_root)
        sel_files = file_selection
        full_rel = sel_files.full_files
        excerpted_rel = [f for f in sel_files.excerpted_files if to_language(f)]
        full_abs = converter.to_absolute(full_rel)
        excerpted_abs = converter.to_absolute(excerpted_rel)
        return ContextGenerator(
            collector,
            spec,
            project_root,
            converter,
            full_rel,
            full_abs,
            excerpted_rel,
            excerpted_abs,
            settings,
            tagger,
        )

    def focus_help(self) -> str:
        rule_provider = RuleProvider.create(self.spec.project_layout)
        return rule_provider.get_rule_content("lc/ins-rule-framework") or ""

    def files(self, in_files: list[str] = []) -> str:
        rel_paths = in_files if in_files else self.full_rel
        return self._render("files", {"files": self.collector.files(rel_paths)})

    def excerpts(self, template_id: str = "excerpts") -> str:
        excerpts = self.collector.excerpts(self.tagger, self.excerpted_rel, self.spec.rule)
        context = {"excerpts": excerpts.excerpts}
        return self._render(template_id, context)

    def definitions(self, requests, template_id: str = "definitions") -> str:
        context = {"definitions": self.collector.definitions(self.tagger, requests)}
        return self._render(template_id, context)

    def prompt(self, template_id: str = "prompt") -> str:
        descriptor = self.spec.rule
        layout = self.spec.project_layout
        context = {
            "prompt": descriptor.get_instructions(),
            "user_notes": descriptor.get_user_notes(layout),
        }
        return self._render(template_id, context)

    def context(self, template_id: str = "context") -> tuple[str, float]:
        descriptor = self.spec.rule
        layout = self.spec.project_layout
        excerpts = self.collector.excerpts(self.tagger, self.excerpted_rel, descriptor)
        implementations = self.collector.definitions(self.tagger, descriptor.implementations)
        files = self.collector.files(self.full_rel)
        settings = self.settings
        context_timestamp = datetime.now().timestamp()
        context = {
            "project_name": self.project_root.name,
            "context_timestamp": context_timestamp,
            "abs_root_path": str(self.project_root),
            "overview": self.collector.overview(
                descriptor.overview,
                self.full_abs,
                self.excerpted_abs,
                [],
                descriptor.get_ignore_patterns("overview"),
            ),
            "overview_mode": descriptor.overview,
            "files": files,
            "excerpts": excerpts.excerpts,
            "sample_definitions": excerpts.metadata["sample_definitions"],
            "implementations": implementations,
            "sample_requested_files": self.converter.to_relative(
                self.collector.sample_file_abs(self.full_abs)
            ),
            "prompt": descriptor.get_instructions() if settings.with_prompt else None,
            "project_notes": descriptor.get_project_notes(layout),
            "tools_available": settings.tools_available,
            "user_notes": descriptor.get_user_notes(layout) if settings.with_user_notes else None,
            "rule_included_paths": set(),
        }
        return self._render(template_id, context), context_timestamp

    def _render(self, template_id: str, context: dict) -> str:
        template_name = self.spec.templates[template_id]
        template = Template.create(template_name, context, self.spec.project_layout.templates_path)
        return template.render()
