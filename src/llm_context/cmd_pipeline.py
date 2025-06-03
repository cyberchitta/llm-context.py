import os
import sys
import traceback
from dataclasses import dataclass
from functools import wraps
from logging import ERROR, INFO
from pathlib import Path
from typing import Callable, Optional

import pyperclip  # type: ignore

from llm_context.exceptions import LLMContextError
from llm_context.exec_env import ExecutionEnvironment
from llm_context.utils import _format_size, log


@dataclass(frozen=True)
class ExecutionResult:
    content: Optional[str]
    env: ExecutionEnvironment


def ensure_utf8_io():
    if sys.platform.startswith("win"):
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def with_env(func: Callable[..., ExecutionResult]) -> Callable[..., ExecutionResult]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> ExecutionResult:
        ensure_utf8_io()
        env = ExecutionEnvironment.create(Path.cwd())
        with env.activate():
            return func(*args, env=env, **kwargs)

    return wrapper


def with_clipboard(func: Callable[..., ExecutionResult]) -> Callable[..., ExecutionResult]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> ExecutionResult:
        result = func(*args, **kwargs)
        if result.content:
            pyperclip.copy(result.content)
            size_bytes = len(result.content.encode("utf-8"))
            result.env.logger.info(f"Copied {_format_size(size_bytes)} to clipboard")
        return result

    return wrapper


def with_print(func: Callable[..., ExecutionResult]) -> Callable[..., ExecutionResult]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> ExecutionResult:
        result = func(*args, **kwargs)
        for msg in result.env.runtime.messages:
            print(msg)
        return result

    return wrapper


def with_error(func: Callable[..., ExecutionResult]) -> Callable[..., None]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        try:
            func(*args, **kwargs)
        except LLMContextError as e:
            log(ERROR, f"Error: {e.message}")
        except Exception as e:
            log(ERROR, f"An unexpected error occurred: {str(e)}")
            traceback.print_exc()

    return wrapper


def create_clipboard_cmd(func: Callable[..., ExecutionResult]) -> Callable[..., None]:
    return with_error(with_print(with_clipboard(with_env(func))))


def create_command(func: Callable[..., ExecutionResult]) -> Callable[..., None]:
    return with_error(with_print(with_env(func)))
