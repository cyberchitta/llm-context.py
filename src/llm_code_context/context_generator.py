import os
from pathlib import Path
from typing import Dict, List, Optional

import pyperclip

from llm_code_context.config_manager import ConfigManager
from llm_code_context.folder_structure_diagram import get_fs_diagram
from llm_code_context.template import Template
from llm_code_context.path_converter import PathConverter


def _format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


class ContextGenerator:
    @staticmethod
    def create():
        return ContextGenerator(ConfigManager.create_default())

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def _context(
        self, file_paths: List[str], fs_diagram: Optional[str] = None, summary: Optional[str] = None
    ) -> Dict:
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

    def files(self, file_paths: List[str]) -> str:
        template_name = self.config_manager.project["templates"]["selfiles"]
        context = self._context(file_paths)
        return self._render(template_name, context)

    def context(self, file_paths: List[str], fs_diagram: str, summary: Optional[str]) -> str:
        template_name = self.config_manager.project["templates"]["context"]
        context = self._context(file_paths, fs_diagram, summary)
        return self._render(template_name, context)

    def _render(self, template_name, context) -> str:
        template = Template.create(template_name, context, self.config_manager.templates_path())
        return template.render()


def _files(in_files: List[str] = None) -> str:
    context_generator = ContextGenerator.create()
    cm = context_generator.config_manager
    path_converter = PathConverter(cm.project_root_path())
    if in_files is not None and not path_converter.validate(in_files):
        print("Invalid file paths")
        return
    files = cm.get_files() if in_files is None else path_converter.to_absolute(in_files)
    return context_generator.files(files)


def _context():
    context_generator = ContextGenerator.create()
    files = context_generator.config_manager.get_files()
    fs_diagram = get_fs_diagram()
    summary = context_generator.config_manager.get_summary()
    return context_generator.context(files, fs_diagram, summary)


def size_feedback(content: str):
    if content is None:
        print("No content to copy")
    else:
        bytes_copied = len(content.encode("utf-8"))
        print(f"Copied {_format_size(bytes_copied)} to clipboard")


def files_from_scratch():
    text = _files()
    pyperclip.copy(text)
    size_feedback(text)


def files_from_clip():
    files = pyperclip.paste().strip().split("\n")
    text = _files(files)
    pyperclip.copy(text)
    size_feedback(text)


def context():
    text = _context()
    pyperclip.copy(text)
    size_feedback(text)


def main():
    files_from_scratch()


if __name__ == "__main__":
    main()
