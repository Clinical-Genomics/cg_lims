from typing import List

from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingQualityChecker
from mock import Mock


def test_quality_control_of_flow_cell_with_all_passing(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_passing_metrics_response: Mock,
    mocker,
):
    # GIVEN a flow cell where all samples passes the quality control
    mocker.patch("requests.get", return_value=novaseq_passing_metrics_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN no samples should fail the quality control
    assert sequencing_quality_checker.failed_qc_count == 0


def test_all_samples_fail_q30(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_q30_fail_response: Mock,
    novaseq_sample_ids: List[str],
    novaseq_lanes,
    mocker,
):
    # GIVEN a flow cell where all samples fail the quality control on Q30
    mocker.patch("requests.get", return_value=novaseq_q30_fail_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN all samples in all lanes should fail the quality control
    expected_fails: int = novaseq_lanes * len(novaseq_sample_ids)
    assert sequencing_quality_checker.failed_qc_count == expected_fails


def test_all_samples_have_too_few_reads(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_reads_fail_response: Mock,
    novaseq_sample_ids: List[str],
    novaseq_lanes: int,
    mocker,
):
    # GIVEN a flow cell where all samples in all lanes have too few reads
    mocker.patch("requests.get", return_value=novaseq_reads_fail_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN all samples in all lanes should fail the quality control
    expected_fails: int = novaseq_lanes * len(novaseq_sample_ids)
    assert sequencing_quality_checker.failed_qc_count == expected_fails


def test_some_samples_fail_quality_control(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_two_failing_metrics_response: Mock,
    mocker,
):
    # GIVEN a flow cell where some samples fail the quality control
    mocker.patch("requests.get", return_value=novaseq_two_failing_metrics_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN some samples in all lanes should fail the quality control
    assert sequencing_quality_checker.failed_qc_count == 2


def test_metrics_missing_for_samples_in_lane(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_missing_metrics_for_sample_in_lane_response: Mock,
    missing_sample_id: str,
    missing_lane: int,
    mocker,
):
    # GIVEN metrics missing data for a sample in lims
    mocker.patch("requests.get", return_value=novaseq_missing_metrics_for_sample_in_lane_response)

    # WHEN validating the sequencing quality
    summary: str = sequencing_quality_checker.validate_sequencing_quality()

    # THEN the sample with missing metrics should fail qc
    assert sequencing_quality_checker.failed_qc_count == 1

    # THEN the missing metrics should be reported
    missing_sample = str((missing_sample_id, missing_lane))
    assert missing_sample in summary


def test_sample_missing_in_lims(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_metrics_with_extra_sample_response: Mock,
    sample_id_missing_in_lims: str,
    mocker,
):
    # GIVEN metrics with a sample not in lims
    mocker.patch("requests.get", return_value=novaseq_metrics_with_extra_sample_response)

    # WHEN validating the sequencing quality
    summary: str = sequencing_quality_checker.validate_sequencing_quality()

    # THEN all samples pass the quality control
    assert sequencing_quality_checker.failed_qc_count == 0

    # THEN the missing sample should be reported
    assert sample_id_missing_in_lims in summary
