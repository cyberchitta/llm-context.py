import os
from dataclasses import dataclass
from pathlib import Path

import pyperclip  # type: ignore
from jinja2 import Environment, FileSystemLoader

from llm_context.config_manager import ConfigManager
from llm_context.folder_structure_diagram import get_fs_diagram
from llm_context.highlighter.language_mapping import to_language
from llm_context.highlighter.outliner import generate_outlines
from llm_context.highlighter.parser import Source


def _format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


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
    config_manager: ConfigManager

    @staticmethod
    def create() -> "ContextGenerator":
        return ContextGenerator(ConfigManager.create_default())

    def _context(
        self, file_paths: list[str], fs_diagram: str | None = None, summary: str | None = None
    ) -> dict:
        root_name = os.path.basename(self.config_manager.project_root_path())
        items = [
            {
                "path": f"/{root_name}/{Path(path).relative_to(self.config_manager.project_root_path())}",
                "content": Path(path).read_text(),
            }
            for path in file_paths
        ]
        return (
            {"items": items}
            | ({"folder_structure_diagram": fs_diagram} if fs_diagram is not None else {})
            | ({"summary": summary} if summary is not None else {})
        )

    def files(self, file_paths: list[str]) -> str:
        context = self._context(file_paths)
        return self._render("selfiles", context)

    def context(self, file_paths: list[str], fs_diagram: str, summary: str | None) -> str:
        context = self._context(file_paths, fs_diagram, summary)
        return self._render("context", context)

    def outlines(self, file_paths: list[str]) -> str:
        source_set = [Source(path, Path(path).read_text()) for path in file_paths]
        outlines = generate_outlines(source_set)
        context = {"items": outlines} if outlines else {"items": []}
        return self._render("outlines", context)

    def _render(self, template_id: str, context: dict) -> str:
        template_name = self.config_manager.project["templates"][template_id]
        template = Template.create(template_name, context, self.config_manager.templates_path())
        return template.render()


def _file_list(cm: ConfigManager, in_files: list[str] = []) -> list[str]:
    path_converter = PathConverter(cm.project_root_path())
    if in_files and not path_converter.validate(in_files):
        print("Invalid file paths")
        return []
    return cm.get_files() if not in_files else path_converter.to_absolute(in_files)


def _files(in_files: list[str] = []) -> str:
    context_generator = ContextGenerator.create()
    files = _file_list(context_generator.config_manager, in_files)
    return context_generator.files(files) if files else ""


def _context() -> str:
    context_generator = ContextGenerator.create()
    files = context_generator.config_manager.get_files()
    fs_diagram = get_fs_diagram()
    summary = context_generator.config_manager.get_summary()
    return context_generator.context(files, fs_diagram, summary)


def _outlines(in_files: list[str] = []) -> str:
    context_generator = ContextGenerator.create()
    files = [
        file for file in _file_list(context_generator.config_manager, in_files) if to_language(file)
    ]
    return context_generator.outlines(files) if files else ""


def size_feedback(content: str) -> None:
    if content is None:
        print("No content to copy")
    else:
        bytes_copied = len(content.encode("utf-8"))
        print(f"Copied {_format_size(bytes_copied)} to clipboard")


def files_from_scratch() -> None:
    text = _files()
    pyperclip.copy(text)
    size_feedback(text)


def files_from_clip() -> None:
    files = pyperclip.paste().strip().split("\n")
    text = _files(files)
    pyperclip.copy(text)
    size_feedback(text)


def context():
    text = _context()
    pyperclip.copy(text)
    size_feedback(text)


def outlines():
    text = _outlines()
    pyperclip.copy(text)
    size_feedback(text)


def main():
    files_from_scratch()


if __name__ == "__main__":
    main()
