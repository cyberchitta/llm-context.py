import os
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader


class TemplateProcessor:
    def __init__(self, project_root: str, templates_path: str):
        self.project_root = project_root
        self.env = Environment(loader=FileSystemLoader(templates_path))

    def render_template(self, template_name: str, items: List[Dict[str, str]]) -> str:
        template = self.env.get_template(template_name)
        return template.render(items=items)

    def template_input(self, file_paths: List[str]) -> List[Dict[str, str]]:
        root_name = os.path.basename(self.project_root)
        return [
            {
                "path": f"/{root_name}/{Path(file_path).relative_to(self.project_root)}",
                "content": Path(file_path).read_text(),
            }
            for file_path in file_paths
        ]

    def process_files(self, template_name: str, file_paths: List[str]) -> str:
        return self.render_template(template_name, self.template_input(file_paths))
