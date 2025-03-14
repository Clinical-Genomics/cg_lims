from typing import List

from cg_lims.EPPs.qc.sequencing_quality_checker import IlluminaSequencingQualityChecker
from genologics.lims import Lims
from mock import Mock


def test_quality_control_of_flow_cell_with_all_passing(
    sequencing_quality_checker: IlluminaSequencingQualityChecker,
    novaseq_passing_metrics_response: Mock,
    mocker,
    lims: Lims,
):
    # GIVEN a flow cell with one negative control where all samples passes the quality control
    mocker.patch("requests.get", return_value=novaseq_passing_metrics_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN no samples should fail the quality control
    assert sequencing_quality_checker.failed_qc_count == 0


def test_all_samples_fail_q30(
    sequencing_quality_checker: IlluminaSequencingQualityChecker,
    novaseq_q30_fail_response: Mock,
    novaseq_sample_ids: List[str],
    novaseq_lanes,
    mocker,
    lims: Lims,
):
    # GIVEN a flow cell with one negative control where all samples fail the quality control on Q30
    mocker.patch("requests.get", return_value=novaseq_q30_fail_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN all samples in all lanes should fail the quality control
    expected_fails: int = novaseq_lanes * (len(novaseq_sample_ids) - 1)
    assert sequencing_quality_checker.failed_qc_count == expected_fails


def test_all_samples_have_too_few_reads(
    sequencing_quality_checker: IlluminaSequencingQualityChecker,
    novaseq_reads_fail_response: Mock,
    novaseq_sample_ids: List[str],
    novaseq_lanes: int,
    mocker,
    lims: Lims,
):
    # GIVEN a flow cell with one negative control where all samples in all lanes have too few reads
    mocker.patch("requests.get", return_value=novaseq_reads_fail_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN all samples in all lanes should fail the quality control
    expected_fails: int = novaseq_lanes * (len(novaseq_sample_ids) - 1)
    assert sequencing_quality_checker.failed_qc_count == expected_fails


def test_some_samples_fail_quality_control(
    sequencing_quality_checker: IlluminaSequencingQualityChecker,
    novaseq_two_failing_metrics_response: Mock,
    mocker,
    lims: Lims,
):
    # GIVEN a flow cell with one negative control where some samples (not the NTC) fail the quality control
    mocker.patch("requests.get", return_value=novaseq_two_failing_metrics_response)

    # WHEN validating the sequencing quality
    sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN some samples in all lanes should fail the quality control
    assert sequencing_quality_checker.failed_qc_count == 2


def test_metrics_missing_for_samples_in_lane(
    sequencing_quality_checker: IlluminaSequencingQualityChecker,
    novaseq_missing_metrics_for_sample_in_lane_response: Mock,
    missing_sample_id: str,
    missing_lane: int,
    mocker,
    lims: Lims,
):
    # GIVEN metrics missing data for a sample in lims
    mocker.patch("requests.get", return_value=novaseq_missing_metrics_for_sample_in_lane_response)

    # WHEN validating the sequencing quality
    summary: str = sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN the sample with missing metrics should fail qc
    assert sequencing_quality_checker.failed_qc_count == 1

    # THEN the missing metrics should be reported
    missing_sample = str((missing_sample_id, missing_lane))
    assert missing_sample in summary


def test_sample_missing_in_lims(
    sequencing_quality_checker: IlluminaSequencingQualityChecker,
    novaseq_metrics_with_extra_sample_response: Mock,
    sample_id_missing_in_lims: str,
    mocker,
    lims: Lims,
):
    # GIVEN metrics with a sample not in lims
    mocker.patch("requests.get", return_value=novaseq_metrics_with_extra_sample_response)

    # WHEN validating the sequencing quality
    summary: str = sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN all samples pass the quality control
    assert sequencing_quality_checker.failed_qc_count == 0

    # THEN the missing sample should be reported
    assert sample_id_missing_in_lims in summary
