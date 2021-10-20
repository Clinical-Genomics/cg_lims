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
    calculate_volumes,
)
from cg_lims.exceptions import LimsError

LOG = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "sample_concentration, final_volume, water_volume, sample_volume, qc_flag",
    [
        (20, 15.0, 12.0, 3, QC_PASSED),
        (21, 15.75, 12.75, 3, QC_PASSED),
        (239, 179.25, 176.25, 3, QC_PASSED),
        (243, 182.25, 179.25, 3, QC_PASSED),
        (244, 122.0, 120.0, 2, QC_FAILED),
        (363, 181.5, 179.5, 2, QC_FAILED),
        (364, 91.0, 90.0, 1, QC_FAILED),
        (723, 180.75, 179.75, 1, QC_FAILED),
        (724, 90.5, 90.0, 0.5, QC_FAILED),
        (1443, 180.375, 179.875, 0.5, QC_FAILED),
    ],
)
def test_new_volume_calculation_algorithm(
    artifact_1, sample_concentration, sample_volume, final_volume, water_volume, qc_flag
):
    server("flat_tests")
    artifact_1.udf["Concentration"] = sample_concentration
    result = calculate_volumes(sample_concentration)
    assert result == (final_volume, water_volume, sample_volume, qc_flag)


def test_calculate_final_volume():
    # GIVEN a sample volume and sample concentration
    sample_volume = 19
    sample_concentration = 3.1578947368421053

    # WHEN calculating the final volume
    result = calculate_final_volume(sample_volume, sample_concentration)

    # THEN the correct result should be returned
    assert result == 15


@pytest.mark.parametrize(
    "sample_concentration",
    [
        3,
        None,
    ],
)
def test_maf_calculate_volume_too_low_concentration(
    sample_concentration,
    artifact_1,
    caplog,
):
    # GIVEN a sample with a concentration lower than 4 or no concentration at all
    server("flat_tests")
    if sample_concentration:
        artifact_1.udf["Concentration"] = sample_concentration
    # WHEN calculating the volumes
    artifacts = [artifact_1]
    with pytest.raises(LimsError) as error_message:
        calculate_volume(artifacts)

    # THEN a warning will be  logged and LimsError exception is raised
    assert "Sample concentration too low or missing for sample" in caplog.text
    assert "MAF volume calculations failed" in error_message.value.message


@pytest.mark.parametrize(
    "sample_concentration",
    [
        9000,
    ],
)
def test_maf_calculate_volume_too_high_concentration(
    sample_concentration,
    artifact_1,
    caplog,
):
    # GIVEN a sample with a concentration lower than 4 or no concentration at all
    server("flat_tests")
    artifact_1.udf["Concentration"] = sample_concentration

    # WHEN calculating the volumes
    artifacts = [artifact_1]
    with pytest.raises(LimsError) as error_message:
        calculate_volume(artifacts)

    # THEN a warning will be logged and LimsError exception is raised
    assert "Sample concentration too high for sample" in caplog.text
    assert "MAF volume calculations failed for" in error_message.value.message


@mock.patch("cg_lims.EPPs.udf.calculate.maf_calculate_volume.calculate_final_volume")
@pytest.mark.parametrize(
    "sample_concentration, sample_volume, final_volume",
    [
        (19, 3.1578947368421053, 15.0),
    ],
)
def test_maf_calculate_volume_low_concentration(
    mock_calculate_final_volume,
    sample_concentration,
    sample_volume,
    final_volume,
    artifact_1,
):
    # GIVEN a sample with a concentration between 4 and 20
    server("flat_tests")
    artifact_1.udf["Concentration"] = sample_concentration

    # WHEN calculating the volumes
    mock_calculate_final_volume.return_value = final_volume
    artifacts = [artifact_1]
    calculate_volume(artifacts)

    # THEN the volumes are calculated using calculate_sample_volume and the QC flag should be set
    # to the correct value
    assert artifact_1.qc_flag == QC_FAILED
    mock_calculate_final_volume.assert_called_with(sample_volume, sample_concentration)
    assert artifact_1.udf["Final Volume (uL)"] == final_volume
    assert artifact_1.udf["Volume of sample (ul)"] == sample_volume
    assert artifact_1.udf["Volume H2O (ul)"] == final_volume - sample_volume
