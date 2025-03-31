import random
from dataclasses import dataclass
from datetime import datetime
from logging import ERROR
from pathlib import Path
from typing import Any, Optional, cast

from jinja2 import Environment, FileSystemLoader  # type: ignore

from llm_context.context_spec import ContextSpec
from llm_context.file_selector import FileSelector
from llm_context.flat_diagram import get_flat_diagram
from llm_context.highlighter.language_mapping import to_language
from llm_context.rule import IGNORE_NOTHING, INCLUDE_ALL
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, ProjectLayout, log, safe_read_file


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

    @staticmethod
    def get_outliner():
        try:
            from llm_context.highlighter.outliner import generate_outlines

            return generate_outlines
        except ImportError as e:
            log(
                ERROR,
                f"Outline dependencies not installed. Install with [outline] extra. Error: {e}",
            )
            return None

    @staticmethod
    def create(root_path: Path) -> "ContextCollector":
        return ContextCollector(
            root_path, PathConverter.create(root_path), ProjectLayout(root_path)
        )

    def sample_file_abs(self, full_abs: list[str]) -> list[str]:
        all_abs = set(FileSelector.create(self.root_path, IGNORE_NOTHING, INCLUDE_ALL).get_files())
        incomplete_files = sorted(list(all_abs - set(full_abs)))
        return random.sample(incomplete_files, min(2, len(incomplete_files)))

    def rule_files(self, files: list[str]) -> list[dict[str, str]]:
        return self.files([f"/{self.root_path.name}/{path}" for path in files])

    def rules(self, rules: list[str]) -> list[dict[str, str]]:
        formatted_paths = {f"/{self.root_path.name}/.llm-context/rules/{rule}" for rule in rules}
        return self.files(list(formatted_paths))

    def files(self, rel_paths: list[str]) -> list[dict[str, str]]:
        abs_paths = self.converter.to_absolute(rel_paths)
        return [
            {"path": rel_path, "content": content}
            for rel_path, abs_path in zip(rel_paths, abs_paths)
            if (content := safe_read_file(abs_path)) is not None
        ]

    def outlines(
        self, tagger: Any, rel_paths: list[str]
    ) -> tuple[list[dict[str, str]], list[tuple[str, str]]]:
        abs_paths = self.converter.to_absolute(rel_paths)
        if rel_paths and (outliner := ContextCollector.get_outliner()):
            from llm_context.highlighter.parser import Source

            source_set = [
                Source(rel, content)
                for rel, abs_path in zip(rel_paths, abs_paths)
                if (content := safe_read_file(abs_path)) is not None
            ]
            return cast(
                tuple[list[dict[str, str]], list[tuple[str, str]]], outliner(tagger, source_set)
            )
        else:
            return ([], [])

    def definitions(self, tagger: Any, requests: list[tuple[str, str]]) -> list[dict[str, Any]]:
        if requests and ContextCollector.get_outliner():
            from llm_context.highlighter.parser import Source
            from llm_context.highlighter.tagger import find_definition

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

    def folder_structure_diagram(
        self,
        full_abs: list[str],
        outline_abs: list[str],
        rule_abs: list[str],
        diagram_ignores: list[str],
    ) -> str:
        return get_flat_diagram(self.root_path, full_abs, outline_abs, rule_abs, diagram_ignores)


@dataclass(frozen=True)
class ContextSettings:
    with_prompt: bool = False
    with_user_notes: bool = False

    @staticmethod
    def create(with_prompt: bool, with_user_notes: bool) -> "ContextSettings":
        return ContextSettings(with_prompt, with_user_notes)


@dataclass(frozen=True)
class ContextGenerator:
    collector: ContextCollector
    spec: ContextSpec
    project_root: Path
    converter: PathConverter
    full_rel: list[str]
    full_abs: list[str]
    outline_rel: list[str]
    outline_abs: list[str]
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
        full_abs = converter.to_absolute(full_rel)
        outline_rel = [f for f in sel_files.outline_files if to_language(f)]
        outline_abs = converter.to_absolute(outline_rel)
        return ContextGenerator(
            collector,
            spec,
            project_root,
            converter,
            full_rel,
            full_abs,
            outline_rel,
            outline_abs,
            settings,
            tagger,
        )

    def files(self, in_files: list[str] = []) -> str:
        rel_paths = in_files if in_files else self.full_rel
        return self._render("files", {"files": self.collector.files(rel_paths)})

    def outlines(self, template_id: str = "highlights") -> str:
        context = {"highlights": self.collector.outlines(self.tagger, self.outline_rel)}
        return self._render(template_id, context)

    def definitions(self, requests, template_id: str = "definitions") -> str:
        context = {"definitions": self.collector.definitions(self.tagger, requests)}
        return self._render(template_id, context)

    def prompt(self, template_id: str = "prompt") -> str:
        descriptor = self.spec.rule
        layout = self.spec.project_layout
        context = {
            "prompt": descriptor.get_prompt(layout),
            "user_notes": descriptor.get_user_notes(layout),
            "rules": self.collector.rules(descriptor.rules),
        }
        return self._render(template_id, context)

    def context(self, template_id: str = "context") -> str:
        descriptor = self.spec.rule
        layout = self.spec.project_layout
        outlines, sample_definitions = self.collector.outlines(self.tagger, self.outline_rel)
        rule_files = self.collector.rule_files(descriptor.files)
        files = self.collector.files(self.full_rel)
        file_paths = {item["path"] for item in files}
        rule_file_paths = [item["path"] for item in rule_files]
        context = {
            "project_name": self.project_root.name,
            "context_timestamp": datetime.now().timestamp(),
            "abs_root_path": str(self.project_root),
            "folder_structure_diagram": self.collector.folder_structure_diagram(
                self.full_abs,
                self.outline_abs,
                self.converter.to_absolute(rule_file_paths),
                descriptor.get_ignore_patterns("diagram"),
            ),
            "files": files + [file for file in rule_files if file["path"] not in file_paths],
            "highlights": outlines,
            "sample_definitions": sample_definitions,
            "sample_requested_files": self.converter.to_relative(
                self.collector.sample_file_abs(self.full_abs)
            ),
            "prompt": descriptor.get_prompt(layout) if self.settings.with_prompt else None,
            "project_notes": descriptor.get_project_notes(layout),
            "user_notes": descriptor.get_user_notes(layout)
            if self.settings.with_user_notes
            else None,
            "rules": self.collector.rules(descriptor.rules),
            "rule_included_paths": set(rule_file_paths),
        }
        return self._render(template_id, context)

    def _render(self, template_id: str, context: dict) -> str:
        template_name = self.spec.templates[template_id]
        template = Template.create(template_name, context, self.spec.project_layout.templates_path)
        return template.render()
