import json
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

PROJECT_INFO: str = (
    "This project uses llm-code-context. For more information, visit: "
    "https://github.com/cyberchitta/llm-code-context.py or "
    "https://pypi.org/project/llm-code-context/"
)


class ConfigManager:
    @staticmethod
    def create_default():
        app_name = "llm-code-context"
        app_author = "cyberchitta"

        user_config_path = Path(user_config_dir(app_name, app_author))
        user_file = user_config_path / "config.json"

        project_path = Path.cwd() / ".llm-code-context"

        project_file = project_path / "config.json"
        ConfigManager.ensure_exists_json(
            project_file,
            {
                "__info__": PROJECT_INFO,
                "template": "all-file-contents.j2",
                "gitignores": [".git", ".gitignore", ".llm-code-context/"],
            },
        )

        scratch_file = project_path / "scratch.json"
        ConfigManager.ensure_exists_json(scratch_file, {"files": []})

        gitignore_file = project_path / ".gitignore"
        ConfigManager.ensure_exists_text(gitignore_file, "scratch.json\n")

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
    def ensure_exists_text(file, text):
        if not file.exists():
            file.write_text(text)

    @staticmethod
    def ensure_exists_json(file, json):
        if not file.exists():
            ConfigManager.save(file, json)

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

    def project_path(self):
        return str(Path.cwd())

    def templates_path(self):
        return self.user["templates_path"]

    def select_files(self, files):
        self.scratch["files"] = files
        ConfigManager.save(self.scratch_file, self.scratch)

    def get_files(self):
        return self.scratch.get("files", [])


def main():
    ConfigManager.create_default()


if __name__ == "__main__":
    main()
