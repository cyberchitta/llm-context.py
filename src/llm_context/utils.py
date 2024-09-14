from typing import Callable

import pyperclip  # type: ignore


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
    def entry_point():
        text = func()
        pyperclip.copy(text)
        size_feedback(text)

    return entry_point
