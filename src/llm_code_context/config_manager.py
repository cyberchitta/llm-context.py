import json
import os
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir


class ConfigManager:
    @staticmethod
    def create_default():
        app_name = "llm-context"
        app_author = "restlessronin"
        user_config_path = Path(user_config_dir(app_name, app_author))

        default_project = {
            "template": "all-file-contents.j2",
            "gitignores": [".git"],
            "root_path": str(Path.cwd()),
        }
        default_scratch = {"files": []}

        user_file = user_config_path / "config.json"
        project_file = Path.cwd() / ".llm-context" / "config.json"
        ConfigManager.ensure_exists(project_file, default_project)
        scratch_file = Path.cwd() / ".llm-context" / "scratch.json"
        ConfigManager.ensure_exists(scratch_file, default_scratch)

        return ConfigManager.create(user_file, project_file, scratch_file)

    @staticmethod
    def create(user_file, project_file, scratch_file):
        user = ConfigManager._load(user_file)
        project = ConfigManager._load(project_file)
        scratch = ConfigManager._load(scratch_file)
        return ConfigManager(scratch_file, user, project, scratch)

    @staticmethod
    def _load(file):
        with open(file, "r") as f:
            return json.load(f)

    @staticmethod
    def ensure_exists(file, default):
        if not file.exists():
            ConfigManager.save(file, default)

    @staticmethod
    def save(file, config):
        file.parent.mkdir(parents=True, exist_ok=True)
        with open(file, "w") as f:
            json.dump(config, f, indent=2)

    def __init__(self, scratch_file, user, project, scratch):
        self.scratch_file = scratch_file
        self.user = user
        self.project = project
        self.scratch = scratch

    def templates_path(self):
        return self.user["templates_path"]

    def update_files(self, files):
        self.scratch["files"] = files
        ConfigManager.save(self.scratch_file, self.scratch)

    def get_files(self):
        return self.scratch.get("files", [])


def main():
    ConfigManager.create_default()


if __name__ == "__main__":
    main()
