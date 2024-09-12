import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from llm_code_context import templates

PROJECT_INFO: str = (
    "This project uses llm-context. For more information, visit: "
    "https://github.com/cyberchitta/llm-context.py or "
    "https://pypi.org/project/llm-context/"
)


@dataclass(frozen=True)
class ConfigManager:
    scratch_file: Path
    project: dict[str, Any]
    scratch: dict[str, Any]

    @staticmethod
    def create_default():
        project_path = Path.cwd() / ".llm-context"

        project_file = project_path / "config.json"
        ConfigManager.ensure_exists_json(
            project_file,
            {
                "__info__": PROJECT_INFO,
                "templates": {"selfiles": "sel-file-contents.j2", "context": "full-context.j2"},
                "gitignores": [".git", ".gitignore", ".llm-context/"],
                "summary_file": None,
            },
        )
        scratch_file = project_path / "scratch.json"
        ConfigManager.ensure_exists_json(scratch_file, {"files": []})
        gitignore_file = project_path / ".gitignore"
        ConfigManager.ensure_exists_text(gitignore_file, "scratch.json\n")

        ConfigManager._copy_templates(project_path)

        return ConfigManager.create(project_file, scratch_file)

    @staticmethod
    def create(project_file, scratch_file):
        project = ConfigManager._load(project_file)
        scratch = ConfigManager._load(scratch_file)
        return ConfigManager(scratch_file, project, scratch)

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

    @staticmethod
    def _copy_templates(project_path):
        templates_dir = project_path / "templates"
        if not templates_dir.exists():
            templates_dir.mkdir(parents=True, exist_ok=True)
            template_files = [r for r in resources.contents(templates) if r.endswith(".j2")]
            for template_file in template_files:
                template_content = resources.read_text(templates, template_file)
                dest_file = templates_dir / template_file
                dest_file.write_text(template_content)
                print(f"Copied template {template_file} to {dest_file}")

    def project_root_path(self):
        return Path.cwd()

    def project_root(self):
        return str(self.project_root_path())

    def templates_path(self):
        return self.project_root_path() / ".llm-context" / "templates"

    def select_files(self, files):
        self.scratch["files"] = files
        ConfigManager.save(self.scratch_file, self.scratch)

    def get_files(self):
        return self.scratch.get("files", [])

    def get_summary(self):
        if not self.project.get("summary_file"):
            return None
        summary_file = self.project_root_path() / self.project["summary_file"]
        if summary_file.exists():
            return summary_file.read_text()
        return None


def main():
    ConfigManager.create_default()


if __name__ == "__main__":
    main()
