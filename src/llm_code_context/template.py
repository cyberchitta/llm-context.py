from typing import Dict

from jinja2 import Environment, FileSystemLoader


class Template:
    @staticmethod
    def create(name: str, context: Dict, templates_path) -> "Template":
        env = Environment(loader=FileSystemLoader(str(templates_path)))
        return Template(name, context, env)

    def __init__(self, name: str, context: Dict, env: Environment):
        self.name = name
        self.context = context
        self.env = env

    def render(self) -> str:
        template = self.env.get_template(self.name)
        return template.render(**self.context)
