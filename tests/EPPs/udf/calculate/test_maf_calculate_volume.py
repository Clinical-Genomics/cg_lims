"""Unit tests for cg_lims.EPPs.udf.calculate.maf_calculate_volume"""
import logging

import mock
import pytest
from tests.conftest import server

from cg_lims.EPPs.udf.calculate.maf_calculate_volume import (
    QC_FAILED,
    QC_PASSED,
    calculate_final_volume,
    calculate_volume,
    get_sample_concentration,
)
from cg_lims.exceptions import LimsError

LOG = logging.getLogger(__name__)


def test_get_sample_concentration(artifact_1):
    # GIVEN a sample with a udf "Concentration"
    server("flat_tests")
    artifact_1.udf["Concentration"] = 19

    # WHEN getting the value for that udf
    result = get_sample_concentration(artifact_1)

    # the correct value is returned
    assert result == 19


def test_get_sample_concentration_no_udf(artifact_1):
    # GIVEN a sample without a udf "Concentration"
    server("flat_tests")

    # WHEN getting the value for that udf
    result = get_sample_concentration(artifact_1)

    # THEN None is returned
    assert result is None


def test_calculate_final_volume():
    # GIVEN a sample volume and sample concentration
    sample_volume = 19
    sample_concentration = 3.1578947368421053

    # WHEN calculating the final volume
    result = calculate_final_volume(sample_volume, sample_concentration)

    # THEN the correct result should be returned
    assert result == 15


@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.get_sample_concentration")
@pytest.mark.parametrize(
    "sample_concentration",
    [
        3,
        None,
    ],
)
def test_maf_calculate_volume_too_low_concentration(
    mock_sample_concentration,
    sample_concentration,
    artifact_1,
    caplog,
):
    # GIVEN a sample with a concentration lower than 4 or no concentration at all
    server("flat_tests")
    mock_sample_concentration.return_value = sample_concentration

    # WHEN calculating the volumes
    artifacts = [artifact_1]
    with pytest.raises(LimsError) as error_message:
        calculate_volume(artifacts)

    # THEN a warning will be  logged and LimsError exception is raised
    assert "Sample concentration too low or missing for sample" in caplog.text
    assert "MAF volume calculations failed" in error_message.value.message


@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.get_sample_concentration")
@pytest.mark.parametrize(
    "sample_concentration",
    [
        9000,
    ],
)
def test_maf_calculate_volume_too_high_concentration(
    mock_sample_concentration,
    sample_concentration,
    artifact_1,
    caplog,
):
    # GIVEN a sample with a concentration lower than 4 or no concentration at all
    server("flat_tests")
    mock_sample_concentration.return_value = sample_concentration

    # WHEN calculating the volumes
    artifacts = [artifact_1]
    with pytest.raises(LimsError) as error_message:
        calculate_volume(artifacts)

    # THEN a warning will be  logged and LimsError exception is raised
    assert "Could not calculate sample volume for" in caplog.text
    assert "MAF volume calculations failed for" in error_message.value.message


@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.get_sample_concentration")
@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.calculate_final_volume")
@pytest.mark.parametrize(
    "sample_concentration, sample_volume, final_volume",
    [
        (19, 3.1578947368421053, 15.0),
    ],
)
def test_maf_calculate_volume_low_concentration(
    mock_calculate_final_volume,
    mock_sample_concentration,
    sample_concentration,
    sample_volume,
    final_volume,
    artifact_1,
):
    # GIVEN a sample with a concentration between 4 and 20
    server("flat_tests")
    mock_sample_concentration.return_value = sample_concentration

    # WHEN calculating the volumes
    mock_calculate_final_volume.return_value = final_volume
    artifacts = [artifact_1]
    calculate_volume(artifacts)

    # THEN the volumes are calculated using calculate_sample_volume and the QC flag should be set to the correct value
    assert artifact_1.qc_flag == QC_FAILED
    mock_calculate_final_volume.assert_called_with(sample_volume, sample_concentration)
    assert artifact_1.udf["Final Volume (uL)"] == final_volume
    assert artifact_1.udf["Volume of sample (ul)"] == sample_volume
    assert artifact_1.udf["Volume H2O (ul)"] == final_volume - sample_volume


@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.get_sample_concentration")
@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.calculate_final_volume")
@pytest.mark.parametrize(
    "sample_concentration, sample_volume, final_volume, qc_flag",
    [
        (243, 3.0, 182.25, QC_PASSED),
        (363, 2.0, 181.5, QC_FAILED),
        (723, 1.0, 180.75, QC_FAILED),
        (1443, 0.5, 180.375, QC_FAILED),
    ],
)
def test_maf_calculate_volume(
    mock_calculate_final_volume,
    mock_sample_concentration,
    sample_concentration,
    sample_volume,
    final_volume,
    qc_flag,
    artifact_1,
):
    # GIVEN a sample with a concentration between 244 and 20
    server("flat_tests")
    mock_sample_concentration.return_value = sample_concentration

    # WHEN calculating the volumes
    mock_calculate_final_volume.return_value = final_volume
    artifacts = [artifact_1]
    calculate_volume(artifacts)

    # THEN the volumes are calculated using calculate_sample_volume and the QC flag should be set to the correct value
    assert artifact_1.qc_flag == qc_flag
    assert artifact_1.udf["Final Volume (uL)"] == final_volume
    assert artifact_1.udf["Volume of sample (ul)"] == sample_volume
    assert artifact_1.udf["Volume H2O (ul)"] == final_volume - sample_volume
    mock_calculate_final_volume.assert_called_with(sample_volume, sample_concentration)


@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.get_sample_concentration")
@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.calculate_final_volume")
def test_maf_calculate_volume_final_volume_too_low(
    mock_calculate_final_volume, mock_sample_concentration, artifact_1, caplog
):
    # GIVEN a sample with a concentration between 244 and 20
    server("flat_tests")

    # WHEN calculating the volumes
    artifacts = [artifact_1]
    mock_sample_concentration.return_value = 10
    mock_calculate_final_volume.return_value = 3
    with pytest.raises(LimsError) as error_message:
        calculate_volume(artifacts)

    # THEN a warning will be  logged and LimsError exception is raised
    assert (
        "The final calculated volume is smaller than the minimum final volume for sample"
        in caplog.text
    )
    assert "MAF volume calculations failed for" in error_message.value.message
