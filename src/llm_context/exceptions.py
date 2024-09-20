import functools
import traceback
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class LLMContextError(Exception):
    def __init__(self, message: str, error_type: str):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)

    @staticmethod
    def handle(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except LLMContextError as e:
                print(f"Error: {e.message}")
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                traceback.print_exc()
            raise

        return wrapper
