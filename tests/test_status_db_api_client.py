from typing import Dict, List

from cg_lims.clients.cg.models import SampleLaneSequencingMetrics
from cg_lims.clients.cg.status_db_api import StatusDBAPI
from mock import Mock


def test_get_sequencing_metrics_for_flow_cell(
    status_db_api_client: StatusDBAPI,
    mock_sequencing_metrics_get_response: Mock,
    sequencing_metrics_json: List[Dict],
    mocker,
):
    # GIVEN a json response with sequencing metrics data
    mocker.patch("requests.get", return_value=mock_sequencing_metrics_get_response)

    # WHEN retrieving sequencing metrics for a flow cell
    result = status_db_api_client.get_sequencing_metrics_for_flow_cell("flow_cell_name")

    # THEN a list of the parsed sequencing metrics should be returned
    sequencing_metrics = [
        SampleLaneSequencingMetrics.model_validate(data) for data in sequencing_metrics_json
    ]
    assert result == sequencing_metrics
