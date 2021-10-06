from typing import Optional

from genologics.lims import Lims
from genologics.entities import Artifact, Sample
from pathlib import Path

import pytest
from click.testing import CliRunner

import threading
import time

from limsmock.server import run_server
from pydantic import BaseModel, Field


class IndexProcessUDFModel(BaseModel):
    lot_nr_tagmentation_buffer: str = Field(..., alias="Lot nr: Tagmentation buffer (TD-buffer)")
    lot_nr_tagmentation_enzyme: str = Field(..., alias="Lot nr: Tagmentation enzyme (TDE1)")
    lot_nr_index: str = Field(..., alias="Lot nr: Index")
    lot_nr_pcr_mix: str = Field(..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)")
    pcr_instrument_incubation: str = Field(..., alias="PCR instrument incubation")
    pcr_instrument_amplification: str = Field(..., alias="PCR instrument amplification")
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")


class ProcessUDFModel(BaseModel):
    lot_nr_beads_library_prep: str = Field(..., alias="Lot nr: Beads")
    lot_nr_etoh_library_prep: str = Field(..., alias="Lot nr: EtOH")
    lot_nr_h2o_library_prep: str = Field(..., alias="Lot nr: H2O")


class ArtifactUDFModel(BaseModel):
    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")
    finished_library_average_size: float = Field(..., alias="Average Size (bp)")


class MegedFieldsIndexModel(IndexProcessUDFModel):
    container_name: Optional[str]
    well_position: Optional[str]
    index_name: Optional[str]
    nr_samples: Optional[int]

    class Config:
        allow_population_by_field_name = True


PORT = 8000
HOST = "127.0.0.1"


def server(file_name: str):
    """Starting up a server based on file_path"""

    file_path = f"tests/fixtures/{file_name}"
    thread = threading.Thread(
        target=run_server,
        args=(
            file_path,
            HOST,
            PORT,
        ),
    )
    thread.daemon = True
    thread.start()
    time.sleep(0.1)


@pytest.fixture
def lims() -> Lims:
    """Get genologics lims instance"""

    return Lims(f"http://{HOST}:{PORT}", "dummy", "dummy")


@pytest.fixture
def artifact_1(lims) -> Artifact:
    """Basic artifact with id 1. Containing no udfs.
    Related to sample_1."""

    return Artifact(lims, id="1")


@pytest.fixture
def sample_1(lims) -> Sample:
    """Basic sample with id S1. Containing no udfs.
    Related to artifact_1."""

    return Sample(lims, id="S1")


@pytest.fixture
def artifact_2(lims) -> Artifact:
    """Basic artifact with id 2. Containing no udfs.
    Related to sample_2."""

    return Artifact(lims, id="2")


@pytest.fixture
def sample_2(lims) -> Sample:
    """Basic sample with id S2. Containing no udfs.
    Related to artifact_2."""

    return Sample(lims, id="S2")


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


@pytest.fixture
def hamilton_normalization_file() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/hamilton_normalization.txt"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def hamilton_sars_cov2_pooling_file() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/sars-cov2-hamilton-prep-pooling.txt"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def hamilton_sars_cov2_indexing_file() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/sars-cov2-hamilton-prep-indexing.txt"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture(name="cli_runner")
def fixture_cli_runner() -> CliRunner:
    """Create a CliRunner"""
    return CliRunner()
