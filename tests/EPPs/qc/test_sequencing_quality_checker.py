from typing import List
from genologics.entities import Process

from cg_lims.EPPs.qc.sequencing_quality_checker import (
    SequencingArtifactManager,
    SequencingQualityChecker,
)
from cg_lims.models.sequencing_metrics import SampleLaneSequencingMetrics
from cg_lims.status_db_api import StatusDBAPI
from genologics.lims import Lims


def test_validate_sequencing_quality(
    lims_process_with_novaseq_data: Process,
    status_db_api_client: StatusDBAPI,
    lims: Lims,
    mock_sequencing_metrics_get_response,
    mocker
):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(
        process=lims_process_with_novaseq_data, lims=lims
    )

    # GIVEN a json response with sequencing metrics data
    mocker.patch("requests.get", return_value=mock_sequencing_metrics_get_response)


    # GIVEN a sequencing quality checker
    sequencing_quality_checker: SequencingQualityChecker = SequencingQualityChecker(
        status_db_api=status_db_api_client, artifact_manager=artifact_manager
    )

    # WHEN validating the sequencing quality
    quality_summary = sequencing_quality_checker.validate_sequencing_quality()

    # THEN the returned quality summary should be a string
    assert isinstance(quality_summary, str)
