import os

import pyperclip

from config_manager import ConfigManager
from template_processor import TemplateProcessor


class ContextGenerator:
    @classmethod
    def create(cls):
        config_manager = ConfigManager.create_default()
        template_processor = TemplateProcessor(config_manager.templates_path())
        return cls(config_manager, template_processor)

    def __init__(self, config_manager, template_processor):
        self.config_manager = config_manager
        self.template_processor = template_processor

    def process_files(self):
        project_config = self.config_manager.project
        template_name = project_config["template"]
        file_paths = project_config["files"]

        output = self.template_processor.process_files(template_name, file_paths)
        pyperclip.copy(output)
        return output


def main():
    context_generator = ContextGenerator.create()
    context_generator.process_files()


if __name__ == "__main__":
    main()
