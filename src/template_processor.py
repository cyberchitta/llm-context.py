import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class TemplateProcessor:
    def __init__(self, templates_path):
        self.env = Environment(loader=FileSystemLoader(os.path.expanduser(templates_path)))

    def render_template(self, template_name, items):
        template = self.env.get_template(template_name)
        return template.render(items=items)

    def template_input(self, file_paths):
        file_contents = [Path(file_path).read_text() for file_path in file_paths]
        return [{'path': path, 'content': content} for path, content in zip(file_paths, file_contents)]

    def process_files(self, template_name, file_paths):
        return self.render_template(template_name, self.template_input(file_paths))

