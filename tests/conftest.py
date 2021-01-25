import pytest
from pathlib import Path
from click.testing import CliRunner
from genologics.lims import Lims

import threading
import time

from limsmock.server import run_server

PORT = 8000
HOST = '127.0.0.1'

@pytest.fixture
def server_flat_tests():
    file_path = f"tests/fixtures/flat_tests"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)


@pytest.fixture
def server_test_get_artifacts():
    file_path = f"tests/fixtures/test_get_artifacts"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)


@pytest.fixture
def server_make_kapa_csv():
    file_path = f"tests/fixtures/test_make_kapa_csv"
    thread = threading.Thread(target=run_server, args=(file_path, HOST, PORT,))
    thread.daemon = True
    thread.start()
    time.sleep(0.1)


@pytest.fixture
def server_make_kapa_csv_missing_udfs():
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
