import pytest
from genologics_mock.lims import MockLims
from genologics_mock.entities import (
    MockArtifact,
    MockProcess,
    MockProcessType,
    MockSample,
)
from .helpers import Helpers


@pytest.fixture
def config():
    """Get file path to invalid csv"""

    return "tests/fixtures/config.yaml"


@pytest.fixture
def lims():
    return MockLims()


@pytest.fixture
def sample():
    return MockSample()


@pytest.fixture
def artifact():
    return MockArtifact()


@pytest.fixture
def process():
    return MockProcess()


@pytest.fixture(name="helpers")
def fixture_helpers():
    """Return a class with small helper functions"""
    return Helpers()
