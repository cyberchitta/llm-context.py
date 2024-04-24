import os

import pyperclip

from config_manager import ConfigManager
from template_processor import TemplateProcessor


def process_files(config_manager, template_processor):
    project_config = config_manager.project
    template_name = project_config["template"]
    file_paths = project_config["files"]

    output = template_processor.process_files(template_name, file_paths)
    pyperclip.copy(output)


def main():
    config_manager = ConfigManager.create_default()
    template_processor = TemplateProcessor(config_manager.templates_path())
    process_files(config_manager, template_processor)


if __name__ == "__main__":
    main()
