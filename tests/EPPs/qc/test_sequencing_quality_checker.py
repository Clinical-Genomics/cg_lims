from typing import List
from genologics.entities import Process
from mock import Mock

from cg_lims.EPPs.qc.sequencing_quality_checker import (
    SequencingArtifactManager,
    SequencingQualityChecker,
)
from cg_lims.models.sequencing_metrics import SampleLaneSequencingMetrics
from cg_lims.status_db_api import StatusDBAPI
from genologics.lims import Lims


def test_quality_control_of_flow_cell_with_all_passing(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_passing_metrics_response: Mock,
    mocker
):
    # GIVEN a flow cell where all samples passes the quality control
    mocker.patch("requests.get", return_value=novaseq_passing_metrics_response)


    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN no samples should fail the quality control
    assert sequencing_quality_checker.samples_not_passing_qc_count == 0



def test_quality_control_of_flow_cell_with_all_failing_q30(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_metrics_failing_q30_threshold_response: Mock,
    novaseq_sample_ids: List[str],
    mocker
):
    # GIVEN a flow cell where all samples fail the quality control on Q30
    mocker.patch("requests.get", return_value=novaseq_metrics_failing_q30_threshold_response)


    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN no samples should fail the quality control
    assert sequencing_quality_checker.samples_not_passing_qc_count == len(novaseq_sample_ids)



def test_quality_control_of_flow_cell_with_all_failing_reads(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_metrics_failing_reads_threshold_response: Mock,
    novaseq_sample_ids: List[str],
    mocker
):
    # GIVEN a flow cell where all samples fail the quality control on Q30
    mocker.patch("requests.get", return_value=novaseq_metrics_failing_reads_threshold_response)


    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN no samples should fail the quality control
    assert sequencing_quality_checker.samples_not_passing_qc_count == len(novaseq_sample_ids)

