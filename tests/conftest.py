import pytest


@pytest.fixture
def config():
    """Get file path to invalid csv"""

    return "tests/fixtures/config.yaml"