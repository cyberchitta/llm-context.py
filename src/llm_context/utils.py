from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Union

import pyperclip  # type: ignore

from llm_context.exceptions import LLMContextError


def _format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def size_feedback(content: str) -> None:
    if content is None:
        print("No content to copy")
    else:
        bytes_copied = len(content.encode("utf-8"))
        print(f"Copied {_format_size(bytes_copied)} to clipboard")


def create_entry_point(func: Callable[..., str]) -> Callable[[], None]:
    @LLMContextError.handle
    def clip_entry_point():
        text = func()
        pyperclip.copy(text)
        size_feedback(text)

    return clip_entry_point


def safe_read_file(path: str) -> Optional[str]:
    file_path = Path(path)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return None
    if not file_path.is_file():
        print(f"Not a file: {file_path}")
        return None
    try:
        return file_path.read_text()
    except PermissionError:
        print(f"Permission denied: {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
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
