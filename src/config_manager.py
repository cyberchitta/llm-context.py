import json
import os


class ConfigManager:
    def __init__(self, global_config_file, project_config_file):
        self.global_config_file = global_config_file
        self.project_config_file = project_config_file
        self.default_global_config = {
            "root_path": os.getcwd(),
            "templates_path": os.path.expanduser("~/Github/llm-code-context.py/templates"),
        }
        self.default_project_config = {
            "template": "all-file-contents.j2",
            "files": [],
        }

    def load_config(self, config_file):
        with open(config_file, "r") as file:
            return json.load(file)

    def save_config(self, config_file, config):
        directory = os.path.dirname(config_file)
        os.makedirs(directory, exist_ok=True)
        with open(config_file, "w") as file:
            json.dump(config, file, indent=2)

    def ensure_config_exists(self, config_file, default_config):
        if not os.path.exists(config_file):
            self.save_config(config_file, default_config)

    def get_global_config(self):
        self.ensure_config_exists(self.global_config_file, self.default_global_config)
        return self.load_config(self.global_config_file)

    def get_project_config(self):
        self.ensure_config_exists(self.project_config_file, self.default_project_config)
        return self.load_config(self.project_config_file)
