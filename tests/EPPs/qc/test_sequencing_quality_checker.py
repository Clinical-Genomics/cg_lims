from typing import List

from mock import Mock

from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingQualityChecker


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
    assert sequencing_quality_checker.samples_not_passing_qc_count == 0


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
    assert sequencing_quality_checker.samples_not_passing_qc_count == expected_fails


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
    assert sequencing_quality_checker.samples_not_passing_qc_count == expected_fails


def test_some_samples_fail_quality_control(
    sequencing_quality_checker: SequencingQualityChecker,
    novaseq_two_failing_metrics_response: Mock,
    mocker,
):
    # GIVEN a flow cell where some samples fail the quality control on Q30
    mocker.patch("requests.get", return_value=novaseq_two_failing_metrics_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality()

    # THEN some samples in all lanes should fail the quality control
    assert sequencing_quality_checker.samples_not_passing_qc_count == 2
