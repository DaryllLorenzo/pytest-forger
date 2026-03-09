"""Sample module for testing pytest-forger."""

from datetime import datetime
from typing import Optional, List


def simple_function(x: int, y: int) -> int:
    """Add two numbers together."""
    return x + y


async def async_function(name: str) -> str:
    """An async function that returns a greeting."""
    return f"Hello, {name}!"


class SampleService:
    """A sample service class with dependencies."""

    def __init__(self, repository=None):
        self.repository = repository

    def get_user(self, user_id: int) -> Optional[dict]:
        """Get a user by ID."""
        if self.repository:
            return self.repository.find(user_id)
        return None

    def process_items(self, items: List[str]) -> int:
        """Process a list of items and return count."""
        return len(items)

    def __private_method(self):
        """This should not be extracted."""
        pass

    def _protected_method(self):
        """This should not be extracted."""
        pass


def function_with_defaults(name: str = "default", count: int = 0) -> str:
    """Function with default arguments."""
    return f"{name}: {count}"
