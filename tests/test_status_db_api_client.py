from mock import Mock
from cg_lims.models.api.sequencing_metrics import SequencingMetrics
from cg_lims.status_db_api import StatusDBAPI


def test_get_sequencing_metrics_for_flow_cell(
    status_db_api_client: StatusDBAPI,
    mock_sequencing_metrics_get_response: Mock,
    sequencing_metrics_json,
    mocker,
):
    # GIVEN a json response with sequencing metrics data
    mocker.patch('requests.get', return_value=mock_sequencing_metrics_get_response)

    # WHEN calling get_sequencing_metrics_for_flow_cell method
    result = status_db_api_client.get_sequencing_metrics_for_flow_cell("flowcellname")

    # THEN it should be a list of the parsed sequencing metrics
    sequencing_metrics = [SequencingMetrics.model_validate(data) for data in sequencing_metrics_json]
    assert result == sequencing_metrics
