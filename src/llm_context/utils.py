from dataclasses import dataclass
from datetime import datetime as dt
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, getLogger
from pathlib import Path
from typing import Any, Optional, Union, cast

import yaml


class _NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


@dataclass(frozen=True)
class Yaml:
    @staticmethod
    def load(file_path: Path) -> dict[str, Any]:
        with open(file_path, "r") as f:
            return cast(dict[str, Any], yaml.safe_load(f))

    @staticmethod
    def save(file_path: Path, data: dict[str, Any]):
        with open(file_path, "w") as f:
            yaml.dump(data, f, Dumper=_NoAliasDumper, default_flow_style=False)


@dataclass(frozen=True)
class ProjectLayout:
    root_path: Path

    @property
    def project_config_path(self) -> Path:
        return self.root_path / ".llm-context"

    @property
    def project_notes_path(self) -> Path:
        return self.project_config_path / "lc-project-notes.md"

    @property
    def user_notes_path(self) -> Path:
        return Path.home() / ".llm-context" / "lc-user-notes.md"

    @property
    def config_path(self) -> Path:
        return self.project_config_path / "config.yaml"

    @property
    def state_path(self) -> Path:
        return self.project_config_path / "lc-state.yaml"

    @property
    def state_store_path(self) -> Path:
        return self.project_config_path / "curr_ctx.yaml"

    @property
    def templates_path(self) -> Path:
        return self.project_config_path / "templates"

    def get_template_path(self, template_name: str) -> Path:
        return self.templates_path / template_name

    @property
    def rules_path(self) -> Path:
        return self.project_config_path / "rules"

    def get_rule_path(self, rule_name: str) -> Path:
        return self.rules_path / rule_name


def _format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_age(timestamp: float) -> str:
    delta = dt.now().timestamp() - timestamp
    if delta < 3600:
        return f"{int(delta / 60)}m ago"
    if delta < 86400:
        return f"{int(delta / 3600)}h ago"
    return f"{int(delta / 86400)}d ago"


def size_feedback(content: str) -> None:
    if content is None:
        log(WARNING, "No content to copy")
    else:
        bytes_copied = len(content.encode("utf-8"))
        log(INFO, f"Copied {_format_size(bytes_copied)} to clipboard")


def safe_read_file(path: str) -> Optional[str]:
    file_path = Path(path)
    if not file_path.exists():
        log(ERROR, f"File not found: {file_path}")
        return None
    if not file_path.is_file():
        log(ERROR, f"Not a file: {file_path}")
        return None
    try:
        return file_path.read_text()
    except PermissionError:
        log(ERROR, f"Permission denied: {file_path}")
    except Exception as e:
        log(ERROR, f"Error reading file {file_path}: {str(e)}")
    return None


@dataclass(frozen=True)
class PathConverter:
    root: Path

    @staticmethod
    def create(root: Path) -> "PathConverter":
        return PathConverter(root)

    def validate(self, paths: Union[str, list[str]]) -> bool:
        if isinstance(paths, str):
            return paths.startswith(f"/{self.root.name}/")
        return all(path.startswith(f"/{self.root.name}/") for path in paths)

    def to_absolute(self, relative_paths: list[str]) -> list[str]:
        return [self._convert_single_path(path) for path in relative_paths]

    def to_relative(self, absolute_paths: list[str]) -> list[str]:
        return [self._make_relative(path) for path in absolute_paths]

    def _convert_single_path(self, path: str) -> str:
        return str(self.root / Path(path[len(self.root.name) + 2 :]))

    def _make_relative(self, path: str) -> str:
        return f"/{self.root.name}/{Path(path).relative_to(self.root)}"


def log(level: int, msg: str) -> None:
    from llm_context.exec_env import ExecutionEnvironment

    logger = (
        ExecutionEnvironment.current().logger
        if ExecutionEnvironment.has_current()
        else getLogger("llm-context-fallback")
    )
    if level == ERROR:
        logger.error(msg)
    elif level == WARNING:
        logger.warning(msg)
    elif level == INFO:
        logger.info(msg)
    elif level == DEBUG:
        logger.debug(msg)
    elif level == CRITICAL:
        logger.critical(msg)
