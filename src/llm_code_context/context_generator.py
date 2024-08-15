import os

import pyperclip

from llm_code_context.config_manager import ConfigManager
from llm_code_context.template_processor import TemplateProcessor


class ContextGenerator:
    @classmethod
    def create(cls):
        config_manager = ConfigManager.create_default()
        template_processor = TemplateProcessor(
            config_manager.project_path(), config_manager.templates_path()
        )
        return cls(config_manager, template_processor)

    def __init__(self, config_manager, template_processor):
        self.config_manager = config_manager
        self.template_processor = template_processor

    def process_files(self):
        config_manager = self.config_manager
        template_name = config_manager.project["template"]
        file_paths = config_manager.scratch["files"]
        output = self.template_processor.process_files(template_name, file_paths)
        pyperclip.copy(output)
        return output


def main():
    context_generator = ContextGenerator.create()
    context_generator.process_files()


if __name__ == "__main__":
    main()
