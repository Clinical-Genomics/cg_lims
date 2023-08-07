import datetime as dt
from typing import Callable, Dict, List, Optional
from genologics.lims import Lims
from genologics.entities import Artifact, Process, Sample
from pathlib import Path
from mock import Mock

import pytest
from click.testing import CliRunner

import threading
import time
from cg_lims.EPPs.qc.sequencing_artifact_manager import SequencingArtifactManager
from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingQualityChecker
from cg_lims.models.sequencing_metrics import SampleLaneSequencingMetrics
from cg_lims.status_db_api import StatusDBAPI

from limsmock.server import run_server
from pydantic.v1 import BaseModel, Field

from tests.fixtures.flowcell_document import FLOW_CELL_DOCUMENT

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

    file_path = "tests/fixtures/Enzymatic_fragmentation.csv"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def kapa_library_preparation_file() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/KAPA_Library_Preparation.csv"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def kapa_library_preparation_file_missing_udf() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/KAPA_Library_Preparation_missing_udf.csv"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def hamilton_normalization_csv() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/hamilton_normalization_csv.txt"
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


@pytest.fixture
def hamilton_buffer_exchange() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/buffer_exchange_hamilton.txt"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def hamilton_buffer_exchange_no_udf() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/buffer_exchange_hamilton_no_udf.txt"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def flow_cell_fixture() -> dict:
    return FLOW_CELL_DOCUMENT


@pytest.fixture
def barcode_tubes_csv() -> str:
    """Get file path to valid json"""

    file_path = "tests/fixtures/barcode_tubes_csv.txt"
    file = Path(file_path)
    return file.read_text()


@pytest.fixture
def lims_process_with_novaseq_data(lims) -> Process:
    """Return lims process populated with the data in fixtures/novaseq_standard."""
    server("novaseq_standard")
    return Process(lims=lims, id="24-308986")


@pytest.fixture
def status_db_api_client() -> StatusDBAPI:
    return StatusDBAPI("http://testbaseurl.com")


@pytest.fixture
def sequencing_metrics_json() -> List[Dict]:
    return [
        {
            "flow_cell_name": "test",
            "flow_cell_lane_number": 1,
            "sample_internal_id": "test",
            "sample_total_reads_in_lane": 100,
            "sample_base_fraction_passing_q30": 0.95,
            "sample_base_mean_quality_score": 30.0,
            "created_at": "2022-01-01T00:00:00",
        }
    ]


@pytest.fixture
def mock_sequencing_metrics_get_response(sequencing_metrics_json) -> Mock:
    mock_response = Mock()
    mock_response.json.return_value = sequencing_metrics_json
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.fixture
def novaseq_flow_cell_name() -> str:
    return "FC A Barbara 220321"


@pytest.fixture
def novaseq_sample_ids() -> List[str]:
    return ["ACC9628A1", "ACC9628A2", "ACC9628A3"]


@pytest.fixture
def novaseq_lanes() -> int:
    return 2


@pytest.fixture
def mock_response() -> Callable:
    def _mock_response(json_return_value):
        mock_response = Mock()
        mock_response.json.return_value = json_return_value
        mock_response.raise_for_status.return_value = None
        return mock_response

    return _mock_response


def generate_metrics_json(
    flow_cell_name: str,
    sample_ids: List[str],
    lanes: int,
    total_reads_in_lane: int,
    base_fraction_passing_q30: float,
) -> List[Dict]:
    metrics = []
    for sample_id in sample_ids:
        for lane in range(1, lanes + 1):
            metric = {
                "flow_cell_name": flow_cell_name,
                "flow_cell_lane_number": lane,
                "sample_internal_id": sample_id,
                "sample_total_reads_in_lane": total_reads_in_lane,
                "sample_base_fraction_passing_q30": base_fraction_passing_q30,
                "sample_base_mean_quality_score": 100,
                "created_at": dt.datetime.now().isoformat(),
            }
            metrics.append(metric)
    return metrics


@pytest.fixture
def novaseq_metrics_passing_thresholds_json(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    return generate_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_fraction_passing_q30=1,
    )


@pytest.fixture
def novaseq_metrics_failing_q30_threshold_json(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    return generate_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_fraction_passing_q30=0,
    )


@pytest.fixture
def novaseq_metrics_failing_reads_json(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    return generate_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=0,
        base_fraction_passing_q30=1,
    )


@pytest.fixture
def novaseq_metrics_two_failing(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    metrics = generate_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_fraction_passing_q30=1,
    )

    metrics[0]["sample_base_fraction_passing_q30"] = 0
    metrics[1]["sample_total_reads_in_lane"] = 0

    return metrics


@pytest.fixture
def missing_sample_id(novaseq_sample_ids: List[str]) -> str:
    return novaseq_sample_ids[0]


@pytest.fixture
def sample_id_missing_in_lims() -> str:
    return "sample_id_missing_in_lims"


@pytest.fixture
def missing_lane():
    return 1


@pytest.fixture
def novaseq_metrics_missing_for_sample_in_lane(
    novaseq_flow_cell_name,
    novaseq_sample_ids,
    novaseq_lanes,
    missing_sample_id,
    missing_lane,
) -> List[Dict]:
    metrics: List[SampleLaneSequencingMetrics] = generate_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_fraction_passing_q30=1,
    )
    for metric in metrics:
        if metric["flow_cell_lane_number"] == missing_lane and metric["sample_internal_id"] == missing_sample_id:
            metrics.remove(metric)
    return metrics


@pytest.fixture
def novaseq_missing_sample(
    novaseq_flow_cell_name,
    novaseq_sample_ids: List[str],
    novaseq_lanes,
    sample_id_missing_in_lims,
) -> List[Dict]:
    novaseq_sample_ids.append(sample_id_missing_in_lims)

    metrics: List[SampleLaneSequencingMetrics] = generate_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_fraction_passing_q30=1,
    )
    return metrics


@pytest.fixture
def novaseq_passing_metrics_response(
    novaseq_metrics_passing_thresholds_json, mock_response
) -> Mock:
    return mock_response(novaseq_metrics_passing_thresholds_json)


@pytest.fixture
def novaseq_q30_fail_response(
    novaseq_metrics_failing_q30_threshold_json, mock_response
) -> Mock:
    return mock_response(novaseq_metrics_failing_q30_threshold_json)


@pytest.fixture
def novaseq_reads_fail_response(
    novaseq_metrics_failing_reads_json, mock_response
) -> Mock:
    return mock_response(novaseq_metrics_failing_reads_json)


@pytest.fixture
def novaseq_two_failing_metrics_response(
    novaseq_metrics_two_failing, mock_response
) -> Mock:
    return mock_response(novaseq_metrics_two_failing)


@pytest.fixture
def novaseq_missing_metrics_for_sample_in_lane_response(
    novaseq_metrics_missing_for_sample_in_lane, mock_response
) -> Mock:
    return mock_response(novaseq_metrics_missing_for_sample_in_lane)


@pytest.fixture
def novaseq_metrics_with_extra_sample_response(
    novaseq_missing_sample, mock_response
) -> Mock:
    return mock_response(novaseq_missing_sample)


@pytest.fixture
def sequencing_quality_checker(
    lims_process_with_novaseq_data: Process,
    lims: Lims,
    status_db_api_client: StatusDBAPI,
) -> SequencingQualityChecker:
    artifact_manager = SequencingArtifactManager(
        process=lims_process_with_novaseq_data, lims=lims
    )

    return SequencingQualityChecker(
        cg_api_client=status_db_api_client, artifact_manager=artifact_manager
    )
