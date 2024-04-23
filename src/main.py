import os

import pyperclip

from config_manager import ConfigManager
from template_processor import TemplateProcessor


def process_files(config_manager, template_processor):
    project_config = config_manager.get_project_config()
    template_name = project_config["template"]
    file_paths = project_config["files"]

    output = template_processor.process_files(template_name, file_paths)
    pyperclip.copy(output)


def main():
    global_config_file = os.path.expanduser("~/.llm-context/config.json")
    project_config_file = ".llm-context/config.json"

    config_manager = ConfigManager(global_config_file, project_config_file)
    template_processor = TemplateProcessor(
        config_manager.get_global_config()["templates_path"]
    )
    process_files(config_manager, template_processor)


if __name__ == "__main__":
    main()
