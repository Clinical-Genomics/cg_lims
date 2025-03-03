import datetime as dt
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List

import pytest
from cg_lims.clients.cg.status_db_api import StatusDBAPI
from cg_lims.clients.cg.token_manager import TokenManager
from cg_lims.EPPs.qc.sequencing_artifact_manager import (
    SequencingArtifactManager,
    SmrtCellSampleManager,
)
from cg_lims.EPPs.qc.sequencing_quality_checker import (
    PacBioSequencingQualityChecker,
    SequencingQualityChecker,
)
from click.testing import CliRunner
from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims
from limsmock.server import run_server
from mock import MagicMock, Mock

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
def token_manager():
    service_account_email = "test@email.com"
    service_account_auth_file = "/path/to/auth/file"
    audience = "audience"
    return TokenManager(service_account_email, service_account_auth_file, audience)


@pytest.fixture
def lims_process_with_novaseq_data(lims) -> Process:
    """Return lims process populated with the data in fixtures/novaseq_standard."""
    server("novaseq_standard")
    return Process(lims=lims, id="24-308986")


@pytest.fixture
def mock_token_manager() -> MagicMock:
    mock_token_manager = MagicMock()
    mock_token_manager.get_token.return_value = "mock_token"
    return mock_token_manager


@pytest.fixture
def status_db_api_client(mock_token_manager: MagicMock) -> StatusDBAPI:
    return StatusDBAPI(base_url="http://testbaseurl.com", token_manager=mock_token_manager)


@pytest.fixture
def sequencing_metrics_json() -> List[Dict]:
    return [
        {
            "flow_cell_name": "test",
            "flow_cell_lane_number": 1,
            "sample_internal_id": "test",
            "sample_total_reads_in_lane": 100,
            "sample_base_percentage_passing_q30": 95,
            "sample_base_mean_quality_score": 30.0,
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


def generate_illumina_metrics_json(
    flow_cell_name: str,
    sample_ids: List[str],
    lanes: int,
    total_reads_in_lane: int,
    base_percentage_passing_q30: float,
) -> List[Dict]:
    metrics = []
    for sample_id in sample_ids:
        for lane in range(1, lanes + 1):
            metric = {
                "flow_cell_name": flow_cell_name,
                "flow_cell_lane_number": lane,
                "sample_internal_id": sample_id,
                "sample_total_reads_in_lane": total_reads_in_lane,
                "sample_base_percentage_passing_q30": base_percentage_passing_q30,
                "created_at": dt.datetime.now().isoformat(),
            }
            metrics.append(metric)
    return metrics


@pytest.fixture
def novaseq_metrics_passing_thresholds_json(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    return generate_illumina_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_percentage_passing_q30=95,
    )


@pytest.fixture
def novaseq_metrics_failing_q30_threshold_json(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    return generate_illumina_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_percentage_passing_q30=0,
    )


@pytest.fixture
def novaseq_metrics_failing_reads_json(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    return generate_illumina_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=0,
        base_percentage_passing_q30=95,
    )


@pytest.fixture
def novaseq_metrics_two_failing(
    novaseq_flow_cell_name, novaseq_sample_ids, novaseq_lanes
) -> List[Dict]:
    metrics = generate_illumina_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_percentage_passing_q30=95,
    )

    metrics[0]["sample_base_percentage_passing_q30"] = 0
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
    metrics: List[Dict] = generate_illumina_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_percentage_passing_q30=95,
    )
    for metric in metrics:
        if (
            metric["flow_cell_lane_number"] == missing_lane
            and metric["sample_internal_id"] == missing_sample_id
        ):
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

    metrics: List[Dict] = generate_illumina_metrics_json(
        flow_cell_name=novaseq_flow_cell_name,
        sample_ids=novaseq_sample_ids,
        lanes=novaseq_lanes,
        total_reads_in_lane=10000,
        base_percentage_passing_q30=95,
    )
    return metrics


@pytest.fixture
def novaseq_passing_metrics_response(
    novaseq_metrics_passing_thresholds_json, mock_response
) -> Mock:
    return mock_response(novaseq_metrics_passing_thresholds_json)


@pytest.fixture
def novaseq_q30_fail_response(novaseq_metrics_failing_q30_threshold_json, mock_response) -> Mock:
    return mock_response(novaseq_metrics_failing_q30_threshold_json)


@pytest.fixture
def novaseq_reads_fail_response(novaseq_metrics_failing_reads_json, mock_response) -> Mock:
    return mock_response(novaseq_metrics_failing_reads_json)


@pytest.fixture
def novaseq_two_failing_metrics_response(novaseq_metrics_two_failing, mock_response) -> Mock:
    return mock_response(novaseq_metrics_two_failing)


@pytest.fixture
def novaseq_missing_metrics_for_sample_in_lane_response(
    novaseq_metrics_missing_for_sample_in_lane, mock_response
) -> Mock:
    return mock_response(novaseq_metrics_missing_for_sample_in_lane)


@pytest.fixture
def novaseq_metrics_with_extra_sample_response(novaseq_missing_sample, mock_response) -> Mock:
    return mock_response(novaseq_missing_sample)


@pytest.fixture
def sequencing_quality_checker(
    lims_process_with_novaseq_data: Process,
    lims: Lims,
    status_db_api_client: StatusDBAPI,
) -> SequencingQualityChecker:
    artifact_manager = SequencingArtifactManager(process=lims_process_with_novaseq_data, lims=lims)

    return SequencingQualityChecker(
        cg_api_client=status_db_api_client, artifact_manager=artifact_manager
    )


@pytest.fixture
def pacbio_smrt_cell_sample_ids() -> Dict[str, List[str]]:
    return {
        "EA157507": ["STG15780A2", "STG15780A6", "STG15780A1"],
        "EA157514": ["STG15780A2", "STG15780A6", "STG15780A1"],
        "EA121040": ["STG15780A5", "STG15780A4"],
        "EA157515": ["STG15780A5", "STG15780A4"],
        "EA157532": ["STG15780A3"],
    }


@pytest.fixture
def missing_pacbio_sample_id(pacbio_smrt_cell_sample_ids: Dict[str, List[str]]) -> str:
    return next(iter(pacbio_smrt_cell_sample_ids.values()))[0]


@pytest.fixture
def missing_smrt_cell_id(pacbio_smrt_cell_sample_ids: Dict[str, List[str]]) -> str:
    return next(iter(pacbio_smrt_cell_sample_ids))


def generate_pacbio_metrics_json(
    smrt_cell_samples: Dict[str, List[str]],
    hifi_mean_read_length: int,
    hifi_median_read_quality: str,
    hifi_reads: int,
    hifi_yield: int,
) -> Dict[str, List[Dict]]:
    metrics: Dict[str, List[Dict]] = {"metrics": []}
    for smrt_cell_id, sample_ids in smrt_cell_samples.items():
        for sample_id in sample_ids:
            metric = {
                "hifi_mean_read_length": hifi_mean_read_length,
                "hifi_median_read_quality": hifi_median_read_quality,
                "hifi_reads": hifi_reads,
                "hifi_yield": hifi_yield,
                "sample_id": sample_id,
                "smrt_cell_id": smrt_cell_id,
            }
            metrics["metrics"].append(metric)
    return metrics


@pytest.fixture
def pacbio_metrics_json(pacbio_smrt_cell_sample_ids) -> Dict[str, List[Dict]]:
    return generate_pacbio_metrics_json(
        smrt_cell_samples=pacbio_smrt_cell_sample_ids,
        hifi_mean_read_length=21000,
        hifi_median_read_quality="Q45",
        hifi_reads=500000,
        hifi_yield=45000000,
    )


@pytest.fixture
def pacbio_metrics_all_failing_json(pacbio_smrt_cell_sample_ids) -> Dict[str, List[Dict]]:
    return generate_pacbio_metrics_json(
        smrt_cell_samples=pacbio_smrt_cell_sample_ids,
        hifi_mean_read_length=12000,
        hifi_median_read_quality="Q13",
        hifi_reads=120000,
        hifi_yield=0,
    )


@pytest.fixture
def pacbio_metrics_missing_sample_json(pacbio_smrt_cell_sample_ids) -> Dict[str, List[Dict]]:
    metrics: Dict[str, List[Dict]] = generate_pacbio_metrics_json(
        smrt_cell_samples=pacbio_smrt_cell_sample_ids,
        hifi_mean_read_length=21000,
        hifi_median_read_quality="Q45",
        hifi_reads=500000,
        hifi_yield=45000000,
    )

    metrics["metrics"].pop(0)

    return metrics


@pytest.fixture
def pacbio_metrics_missing_smrt_cell_json(
    pacbio_smrt_cell_sample_ids, missing_smrt_cell_id
) -> Dict[str, List[Dict]]:
    metrics: Dict[str, List[Dict]] = generate_pacbio_metrics_json(
        smrt_cell_samples=pacbio_smrt_cell_sample_ids,
        hifi_mean_read_length=21000,
        hifi_median_read_quality="Q45",
        hifi_reads=500000,
        hifi_yield=45000000,
    )

    missing_cell_metrics: List[Dict] = []
    for metric in metrics["metrics"]:
        if metric["smrt_cell_id"] != missing_smrt_cell_id:
            missing_cell_metrics.append(metric)
    metrics["metrics"] = missing_cell_metrics

    return metrics


@pytest.fixture
def pacbio_passing_metrics_response(pacbio_metrics_json, mock_response) -> Mock:
    return mock_response(pacbio_metrics_json)


@pytest.fixture
def pacbio_failing_metrics_response(pacbio_metrics_all_failing_json, mock_response) -> Mock:
    return mock_response(pacbio_metrics_all_failing_json)


@pytest.fixture
def pacbio_missing_sample_metrics_response(
    pacbio_metrics_missing_sample_json, mock_response
) -> Mock:
    return mock_response(pacbio_metrics_missing_sample_json)


@pytest.fixture
def pacbio_missing_smrt_cell_metrics_response(
    pacbio_metrics_missing_smrt_cell_json, mock_response
) -> Mock:
    return mock_response(pacbio_metrics_missing_smrt_cell_json)


@pytest.fixture
def pacbio_sequencing_quality_checker(
    lims: Lims,
    status_db_api_client: StatusDBAPI,
) -> PacBioSequencingQualityChecker:
    server("revio_demux_run")
    process: Process = Process(lims=lims, id="24-558673")
    artifact_manager: SmrtCellSampleManager = SmrtCellSampleManager(process=process, lims=lims)

    return PacBioSequencingQualityChecker(
        cg_api_client=status_db_api_client, artifact_manager=artifact_manager
    )
