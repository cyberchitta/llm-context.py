import os
from dataclasses import dataclass
from pathlib import Path

import pyperclip  # type: ignore
from jinja2 import Environment, FileSystemLoader

from llm_context.folder_structure_diagram import get_annotated_fsd
from llm_context.highlighter.language_mapping import to_language
from llm_context.highlighter.outliner import generate_outlines
from llm_context.highlighter.parser import Source
from llm_context.project_settings import ProjectSettings
from llm_context.utils import create_entry_point


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
class PathConverter:
    root: Path

    def validate(self, paths: list[str]) -> bool:
        return all(path.startswith(f"/{self.root.name}/") for path in paths)

    def to_absolute(self, relative_paths: list[str]) -> list[str]:
        if not self.validate(relative_paths):
            raise ValueError("Invalid paths provided")
        return [str(self.root / Path(path[len(self.root.name) + 2 :])) for path in relative_paths]


@dataclass(frozen=True)
class ContextGenerator:
    settings: ProjectSettings

    @staticmethod
    def create() -> "ContextGenerator":
        return ContextGenerator(ProjectSettings.create())

    def _files(self, file_paths: list[str]) -> list[dict[str, str]]:
        root_name = os.path.basename(self.settings.project_root_path)
        return [
            {
                "path": f"/{root_name}/{Path(path).relative_to(self.settings.project_root_path)}",
                "content": Path(path).read_text(),
            }
            for path in file_paths
        ]

    def _outlines(self, file_paths: list[str]) -> list[dict[str, str]]:
        source_set = [Source(path, Path(path).read_text()) for path in file_paths]
        return generate_outlines(source_set)

    def files(self, file_paths: list[str]) -> str:
        path_converter = PathConverter(self.settings.project_root_path)
        if file_paths and not path_converter.validate(file_paths):
            print("Invalid file paths")
            return ""
        valid_paths = path_converter.to_absolute(file_paths)
        paths = (
            valid_paths
            if valid_paths
            else self.settings.context_storage.get_stored_context().get("full", [])
        )
        return self._render("files", {"files": self._files(paths)})

    def context(self) -> str:
        project_root = self.settings.project_root_path
        selected_files = self.settings.context_storage.get_stored_context()
        full_files = selected_files.get("full", [])
        outline_files = [file for file in selected_files.get("outline", []) if to_language(file)]
        context = {
            "folder_structure_diagram": get_annotated_fsd(project_root, full_files, outline_files),
            "summary": self.settings.get_summary(),
            "files": self._files(full_files),
            "highlights": self._outlines(outline_files),
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
