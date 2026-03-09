"""Sample module with external dependencies for testing mock generation."""

import requests
from sqlalchemy import create_engine
from my_custom_lib import SomeClass


def fetch_data(url: str) -> dict:
    """Fetch data from an external API."""
    response = requests.get(url)
    return response.json()


def create_database(db_url: str):
    """Create a database engine."""
    return create_engine(db_url)


def use_custom_library(value: int) -> int:
    """Use a custom library."""
    instance = SomeClass()
    return instance.process(value)
