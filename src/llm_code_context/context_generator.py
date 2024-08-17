import os
from pathlib import Path
from typing import Dict, List, Optional

import pyperclip

from llm_code_context.config_manager import ConfigManager
from llm_code_context.file_selector import FileSelector
from llm_code_context.folder_structure_diagram import get_fs_diagram
from llm_code_context.template import Template


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
        output = template.render()
        pyperclip.copy(output)
        return


def files():
    context_generator = ContextGenerator.create()
    files = context_generator.config_manager.get_files()
    return context_generator.files(files)


def context():
    context_generator = ContextGenerator.create()
    files = context_generator.config_manager.get_files()
    fs_diagram = get_fs_diagram()
    summary = context_generator.config_manager.get_summary()
    return context_generator.context(files, fs_diagram, summary)


def main():
    files()


if __name__ == "__main__":
    main()
