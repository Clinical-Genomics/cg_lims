import pytest
from pathlib import Path
from click.testing import CliRunner
from genologics.lims import Lims
from genologics.entities import Artifact, Sample

import threading
import time

from limsmock.server import run_server

PORT = 8000
HOST = '127.0.0.1'

@pytest.fixture
def server_flat_tests():
    """Fixture for simple tests that don't assume specific nested relations between entities.
    Entities in this fixture should not have any udfs set from the beginning."""

    file_path = f"tests/fixtures/flat_tests"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)


@pytest.fixture
def server_test_get_artifacts():
    """Specific fixture for get_artifacts test. """

    file_path = f"tests/fixtures/test_get_artifacts"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)


@pytest.fixture
def server_make_kapa_csv():
    """Specific fixture for make_kapa_csv test."""

    file_path = f"tests/fixtures/test_make_kapa_csv"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)


@pytest.fixture
def server_make_kapa_csv_missing_udfs():
    """Specific fixture for make_kapa_csv test with missing udfs."""

    file_path = f"tests/fixtures/make_kapa_csv_missing_udfs"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)

@pytest.fixture
def lims():
    """Get genologics lims instance"""

    lims = Lims(f"http://{HOST}:{PORT}", 'dummy', 'dummy')
    return lims


@pytest.fixture
def artifact_1(lims):
    """Basic artifact with id 1. Containing no udfs.
    Related to sample_1."""

    artifact = Artifact(lims, id='1')

    return artifact


@pytest.fixture
def sample_1(lims):
    """Basic sample with id S1. Containing no udfs.
    Related to artifact_1."""

    sample = Sample(lims, id='S1')

    return sample


@pytest.fixture
def artifact_2(lims):
    """Basic artifact with id 2. Containing no udfs.
    Related to sample_2."""

    artifact = Artifact(lims, id='2')

    return artifact


@pytest.fixture
def sample_2(lims):
    """Basic sample with id S2. Containing no udfs.
    Related to artifact_2."""

    sample = Sample(lims, id='S2')

    return sample

@pytest.fixture
def config():
    """Get file path to config"""

    return "tests/fixtures/config.yaml"


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


