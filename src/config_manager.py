import json
import os


class ConfigManager:
    user_file = os.path.expanduser("~/.llm-context/config.json")
    project_file_leaf = ".llm-context/config.json"

    @staticmethod
    def create_default():
        default_user = {
            "root_path": os.getcwd(),
            "templates_path": os.path.expanduser("~/Github/llm-context/templates"),
        }
        default_project = {"template": "all-file-contents.j2", "files": [], "gitignores": [".git"]}
        user_file = ConfigManager.user_file
        project_file = ConfigManager.get_project_file(user_file)

        return ConfigManager.create(user_file, project_file, default_user, default_project)

    @staticmethod
    def create(user_file, project_file, default_user, default_project):
        config_manager = ConfigManager(project_file)
        config_manager.ensure_exists(user_file, default_user)
        config_manager.ensure_exists(project_file, default_project)
        config_manager.load(user_file, project_file)
        return config_manager

    @staticmethod
    def get_project_file(user_file):
        user = ConfigManager._load(user_file)
        root_path = user["root_path"]
        return os.path.join(root_path, ConfigManager.project_file_leaf)

    @staticmethod
    def _load(file):
        with open(file, "r") as f:
            return json.load(f)

    def __init__(self, project_file):
        self.project_file = project_file
        self.user = None
        self.project = None

    def ensure_exists(self, file, default):
        if not os.path.exists(file):
            self.save(file, default)

    def load(self, user_file, project_file):
        self.user = self._load(user_file)
        self.project = self._load(project_file)

    def save(self, file, config):
        directory = os.path.dirname(file)
        os.makedirs(directory, exist_ok=True)
        with open(file, "w") as f:
            json.dump(config, f, indent=2)

    def templates_path(self):
        return self.user["templates_path"]

    def update_files(self, files):
        self.project["files"] = files
        self.save(self.project_file, self.project)


def main():
    ConfigManager.create_default()


if __name__ == "__main__":
    main()
