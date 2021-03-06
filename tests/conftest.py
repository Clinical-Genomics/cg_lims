
from genologics.lims import Lims
from genologics.entities import Artifact, Sample
from pathlib import Path

import pytest
from click.testing import CliRunner

import threading
import time

from limsmock.server import run_server

PORT = 8000
HOST = '127.0.0.1'


def server(file_name: str):
    """Starting up a server based on file_path"""

    file_path = f"tests/fixtures/{file_name}"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)

@pytest.fixture
def lims() -> Lims:
    """Get genologics lims instance"""

    return Lims(f"http://{HOST}:{PORT}", 'dummy', 'dummy')


@pytest.fixture
def artifact_1(lims) -> Artifact:
    """Basic artifact with id 1. Containing no udfs.
    Related to sample_1."""

    artifact = Artifact(lims, id='1')

    return artifact


@pytest.fixture
def sample_1(lims) -> Sample:
    """Basic sample with id S1. Containing no udfs.
    Related to artifact_1."""

    sample = Sample(lims, id='S1')

    return sample


@pytest.fixture
def artifact_2(lims) -> Artifact:
    """Basic artifact with id 2. Containing no udfs.
    Related to sample_2."""

    artifact = Artifact(lims, id='2')

    return artifact


@pytest.fixture
def sample_2(lims) -> Sample:
    """Basic sample with id S2. Containing no udfs.
    Related to artifact_2."""

    sample = Sample(lims, id='S2')

    return sample


@pytest.fixture
def config() -> Path:
    """Get file path to config"""

    return Path("tests/fixtures/config.yaml")


@pytest.fixture
def enzymatic_fragmentation_file() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/Enzymatic_fragmentation"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def kapa_library_preparation_file() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/KAPA_Library_Preparation"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def kapa_library_preparation_file_missing_udf() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/KAPA_Library_Preparation_missing_udf"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture(name="cli_runner")
def fixture_cli_runner() -> CliRunner:
    """Create a CliRunner"""
    runner = CliRunner()
    return runner
