from importlib import resources
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

from llm_code_context import templates
from llm_code_context.config_manager import ConfigManager


class Initializer:
    def __init__(self):
        self.app_name = "llm-code-context"
        self.app_author = "cyberchitta"
        self.user_config_path = Path(user_config_dir(self.app_name, self.app_author))
        self.user_data_path = Path(user_data_dir(self.app_name, self.app_author))
        self.user_config_file = self.user_config_path / "config.json"
        self.templates_dir = self.user_data_path / "templates"

    def initialize(self):
        self._create_user_config()
        self._copy_templates()

    def _create_user_config(self):
        if not self.user_config_file.exists():
            default_user = {
                "templates_path": str(self.templates_dir),
            }
            ConfigManager.save(self.user_config_file, default_user)
            print(f"Created user configuration at {self.user_config_file}")

    def _copy_templates(self):
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            template_files = [r for r in resources.contents(templates) if r.endswith(".j2")]
            for template_file in template_files:
                template_content = resources.read_text(templates, template_file)
                dest_file = self.templates_dir / template_file
                dest_file.write_text(template_content)
                print(f"Copied template {template_file} to {dest_file}")


def initialize():
    initializer = Initializer()
    initializer.initialize()


if __name__ == "__main__":
    initialize()
