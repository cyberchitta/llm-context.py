import random
from dataclasses import dataclass
from pathlib import Path

import pyperclip  # type: ignore
from jinja2 import Environment, FileSystemLoader

from llm_context.file_selector import FileSelector
from llm_context.folder_structure_diagram import get_annotated_fsd
from llm_context.highlighter.language_mapping import to_language
from llm_context.highlighter.outliner import generate_outlines
from llm_context.highlighter.parser import Source
from llm_context.project_settings import ProjectSettings
from llm_context.utils import PathConverter, create_entry_point, safe_read_file


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
class ContextGenerator:
    settings: ProjectSettings

    @staticmethod
    def create() -> "ContextGenerator":
        return ContextGenerator(ProjectSettings.create())

    def _sample_file_abs(self, full_abs: set[str]) -> list[str]:
        all_abs = set(FileSelector.create(self.settings.project_root_path, [".git"]).get_files())
        incomplete_files = sorted(list(all_abs - set(full_abs)))
        return random.sample(incomplete_files, min(2, len(incomplete_files)))

    def _files(self, rel_paths: list[str]) -> list[dict[str, str]]:
        abs_paths = PathConverter.create(self.settings.project_root_path).to_absolute(rel_paths)
        return [
            {"path": rel_path, "content": content}
            for rel_path, abs_path in zip(rel_paths, abs_paths)
            if (content := safe_read_file(abs_path)) is not None
        ]

    def _outlines(self, rel_paths: list[str]) -> list[dict[str, str]]:
        abs_paths = PathConverter.create(self.settings.project_root_path).to_absolute(rel_paths)
        source_set = [
            Source(rel, content)
            for rel, abs_path in zip(rel_paths, abs_paths)
            if (content := safe_read_file(abs_path)) is not None
        ]
        return generate_outlines(source_set)

    def files(self, rel_paths: list[str]) -> str:
        converter = PathConverter.create(self.settings.project_root_path)
        if rel_paths and not converter.validate(rel_paths):
            print("Invalid file paths")
            return ""
        paths = (
            rel_paths
            if rel_paths
            else self.settings.context_storage.get_stored_context().get("full", [])
        )
        return self._render("files", {"files": self._files(paths)})

    def context(self) -> str:
        project_root = self.settings.project_root_path
        converter = PathConverter.create(project_root)
        sel_files = self.settings.context_storage.get_stored_context()
        full_abs = converter.to_absolute(full_rel := sel_files.get("full", []))
        outline_abs = converter.to_absolute(
            outline_rel := [f for f in sel_files.get("outline", []) if to_language(f)]
        )
        context = {
            "project_name": project_root.name,
            "folder_structure_diagram": get_annotated_fsd(project_root, full_abs, outline_abs),
            "summary": self.settings.get_summary(),
            "files": self._files(full_rel),
            "highlights": self._outlines(outline_rel),
            "sample_requested_files": converter.to_relative(self._sample_file_abs(set(full_abs))),
        }
        return self._render("context", context)

    def _render(self, template_id: str, context: dict) -> str:
        template_name = self.settings.context_config.config["templates"][template_id]
        template = Template.create(
            template_name, context, self.settings.project_layout.templates_path
        )
        return template.render()


def _files(in_files: list[str] = []) -> str:
    return ContextGenerator.create().files(in_files)


def _context() -> str:
    return ContextGenerator.create().context()


files_from_scratch = create_entry_point(lambda: _files())
files_from_clip = create_entry_point(lambda: _files(pyperclip.paste().strip().split("\n")))
context = create_entry_point(_context)


def main():
    files_from_scratch()


if __name__ == "__main__":
    main()
