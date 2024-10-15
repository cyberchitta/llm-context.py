import functools
import traceback
from typing import Any, Callable, TypeVar

# Generic type variable for type hinting
T = TypeVar("T")


# Custom exception class for handling errors specific to the LLMContext
class LLMContextError(Exception):
    def __init__(self, message: str, error_type: str):
        self.message = message  # Error message describing the issue
        self.error_type = error_type  # A string representing the type of error
        super().__init__(self.message)  # Initialize the base Exception class

    # Static method to decorate functions with error handling
    @staticmethod
    def handle(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)  # Preserve the original function's metadata
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)  # Execute the function
            except LLMContextError as e:  # Handle known LLMContextError exceptions
                print(f"Error: {e.message}")  # Print the custom error message
            except Exception as e:  # Handle any other unforeseen exceptions
                print(f"An unexpected error occurred: {str(e)}")  # Print a generic error message
                traceback.print_exc()  # Print the stack trace to help debug
            raise  # Reraise the exception after handling

        return wrapper  # Return the wrapped function

