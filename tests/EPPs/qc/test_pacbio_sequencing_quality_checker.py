from typing import Dict, List

from cg_lims.EPPs.qc.sequencing_quality_checker import PacBioSequencingQualityChecker
from genologics.lims import Lims
from mock import Mock


def test_quality_control_with_all_samples_passing(
    pacbio_sequencing_quality_checker: PacBioSequencingQualityChecker,
    pacbio_passing_metrics_response: Mock,
    mocker,
    lims: Lims,
):
    # GIVEN a run where all samples pass the quality control
    mocker.patch("requests.get", return_value=pacbio_passing_metrics_response)

    # WHEN validating the sequencing quality
    pacbio_sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN no samples should fail the quality control
    assert pacbio_sequencing_quality_checker.failed_qc_count == 0


def test_quality_control_with_all_samples_failing(
    pacbio_sequencing_quality_checker: PacBioSequencingQualityChecker,
    pacbio_failing_metrics_response: Mock,
    mocker,
    lims: Lims,
):
    # GIVEN a run where all samples fail the quality control
    mocker.patch("requests.get", return_value=pacbio_failing_metrics_response)

    # WHEN validating the sequencing quality
    pacbio_sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN no samples should pass the quality control
    assert pacbio_sequencing_quality_checker.failed_qc_count == len(
        pacbio_sequencing_quality_checker.artifact_manager.get_cell_samples_in_lims()
    )


def test_metrics_missing_for_sample(
    pacbio_sequencing_quality_checker: PacBioSequencingQualityChecker,
    pacbio_missing_sample_metrics_response: Mock,
    missing_pacbio_sample_id: str,
    mocker,
    lims: Lims,
):

    # GIVEN missing metrics data for a sample in lims
    mocker.patch("requests.get", return_value=pacbio_missing_sample_metrics_response)

    # WHEN validating the sequencing quality
    summary: str = pacbio_sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN the sample with missing metrics should fail qc
    assert pacbio_sequencing_quality_checker.failed_qc_count == 1

    # THEN the missing metrics should be reported
    assert missing_pacbio_sample_id in summary


def test_metrics_missing_for_smrt_cell(
    pacbio_sequencing_quality_checker: PacBioSequencingQualityChecker,
    pacbio_missing_smrt_cell_metrics_response: Mock,
    pacbio_metrics_missing_smrt_cell_json,
    missing_smrt_cell_id: str,
    pacbio_smrt_cell_sample_ids: Dict[str, List[str]],
    mocker,
    lims: Lims,
):
    # GIVEN missing metrics data for a SMRT Cell in lims
    mocker.patch("requests.get", return_value=pacbio_missing_smrt_cell_metrics_response)

    # WHEN validating the sequencing quality
    summary: str = pacbio_sequencing_quality_checker.validate_sequencing_quality(lims=lims)

    # THEN the samples with missing metrics should fail QC
    assert pacbio_sequencing_quality_checker.failed_qc_count == len(
        pacbio_smrt_cell_sample_ids[missing_smrt_cell_id]
    )

    # THEN the missing metrics should be reported
    assert (
        f"No metrics were found for the following sample sequencing artifacts: [('{missing_smrt_cell_id}"
        in summary
    )
