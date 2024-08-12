import os
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader


class TemplateProcessor:
    def __init__(self, templates_path: str):
        self.env = Environment(loader=FileSystemLoader(templates_path))

    def render_template(self, template_name: str, items: List[Dict[str, str]]) -> str:
        template = self.env.get_template(template_name)
        return template.render(items=items)

    def template_input(self, file_paths: List[str]) -> List[Dict[str, str]]:
        file_contents = [Path(file_path).read_text() for file_path in file_paths]
        return [
            {"path": path, "content": content} for path, content in zip(file_paths, file_contents)
        ]

    def process_files(self, template_name: str, file_paths: List[str]) -> str:
        return self.render_template(template_name, self.template_input(file_paths))
