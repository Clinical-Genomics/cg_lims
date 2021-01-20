import pytest
from pathlib import Path
import json
from click.testing import CliRunner
from genologics_mock.lims import MockLims
from genologics_mock.entities import (
    MockArtifact,
    MockProcess,
    MockSample,
)
from .helpers import Helpers
import threading
import time

############# limsmock server fixtures #############

from limsmock.server import run_server



@pytest.fixture
def server_test_get_artifacts():
    file_path = f"tests/fixtures/test_get_artifacts"
    thread = threading.Thread(target=run_server, args=(file_path,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)

########### ########## ######### ############# #############

@pytest.fixture
def config():
    """Get file path to config"""

    return "tests/fixtures/config.yaml"


@pytest.fixture
def kapa_csv_data():
    """Get file path to make_kapa_csv_data.json"""

    with open("tests/fixtures/make_kapa_csv_data.json") as file:
        return json.load(file)


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


@pytest.fixture
def enzymatic_fragmentation_file():
    """Get file path to valid json"""
    file_path = "tests/fixtures/Enzymatic_fragmentation"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def kapa_library_preparation_file():
    """Get file path to valid json"""
    file_path = "tests/fixtures/KAPA_Library_Preparation"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def kapa_library_preparation_file_missing_udf():
    """Get file path to valid json"""
    file_path = "tests/fixtures/KAPA_Library_Preparation_missing_udf"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture(name="cli_runner")
def fixture_cli_runner():
    """Create a CliRunner"""
    runner = CliRunner()
    return runner
