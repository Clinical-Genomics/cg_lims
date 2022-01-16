"""Unit tests for cg_lims.EPPs.udf.calculate.maf_calculate_volume"""
import logging

import pytest
from genologics.entities import Artifact
from genologics.lims import Lims
from pydantic import ValidationError

from cg_lims.EPPs.udf.calculate.maf_calculate_volume import (
    QC_FAILED,
    QC_PASSED,
    MafVolumes,
    calculate_volume,
)
from tests.conftest import server

LOG = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "sample_concentration, final_volume, water_volume, sample_volume, qc_flag",
    [
        (19, 15.0, 11.842105263157894, 3.1578947368421053, QC_FAILED),
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
def test_maf_volume_model(sample_concentration, sample_volume, final_volume, water_volume, qc_flag):
    # GIVEN a pydantic model for MAF volumes

    # WHEN calculating the volumes in the validators with valid values for 'sample_concentration'
    result = MafVolumes(sample_concentration=sample_concentration)

    # THEN the correct results should be set
    assert result.sample_concentration == sample_concentration
    assert result.final_volume == final_volume
    assert result.water_volume == water_volume
    assert result.sample_volume == sample_volume
    assert result.qc_flag == qc_flag


@pytest.mark.parametrize(
    "sample_concentration",
    [
        3.99,
    ],
)
def test_maf_volume_model_sample_concentration_value_error(sample_concentration):
    # GIVEN a pydantic model for MAF volumes

    # WHEN calculating the volumes in the validators with an invalid value for
    # 'sample_concentration'
    with pytest.raises(ValueError) as error_message:
        MafVolumes(sample_concentration=sample_concentration)

    # THEN the validator for sample_concentration should raise a ValueError exception
    assert error_message.value.errors()[0]["loc"][0] == "sample_concentration"
    assert error_message.value.errors()[0]["type"] == "value_error"
    assert error_message.value.errors()[0]["msg"] == "Too low or missing concentration"


@pytest.mark.parametrize(
    "sample_concentration",
    [
        None,
    ],
)
def test_maf_volume_model_sample_concentration_validation_error(sample_concentration):
    # GIVEN a pydantic model for MAF volumes

    # WHEN calculating the volumes in the validator when there is no 'sample_concentration'
    with pytest.raises(ValidationError) as error_message:
        MafVolumes(sample_concentration=sample_concentration)

    # THEN pydantic should raise a ValidationError exception
    assert error_message.value.errors()[0]["loc"][0] == "sample_concentration"
    assert error_message.value.errors()[0]["type"] == "type_error.none.not_allowed"
    assert error_message.value.errors()[0]["msg"] == "none is not an allowed value"


@pytest.mark.parametrize(
    "sample_concentration",
    [
        9001,
    ],
)
def test_maf_volume_model_sample_volume_value_error(sample_concentration):
    # GIVEN a pydantic model for MAF volumes

    # WHEN calculating the volumes in the validator when there is no 'sample_concentration'
    with pytest.raises(ValueError) as error_message:
        MafVolumes(sample_concentration=sample_concentration)

    # THEN the validator for sample_volume should raise a ValueError exception
    assert error_message.value.errors()[0]["loc"][0] == "sample_volume"
    assert error_message.value.errors()[0]["type"] == "value_error"
    assert error_message.value.errors()[0]["msg"] == "Sample concentration not in valid range"


@pytest.mark.parametrize(
    "sample_concentration, final_volume, water_volume, sample_volume, qc_flag",
    [
        (243, 182.25, 179.25, 3, QC_PASSED),
    ],
)
def test_calculate_volume(
    sample_concentration,
    sample_volume,
    final_volume,
    water_volume,
    qc_flag,
    artifact_1: Artifact,
):
    # GIVEN a sample with a valid sample concentration:
    server("flat_tests")
    artifact_1.udf["Concentration"] = sample_concentration
    artifacts = [artifact_1]

    # WHEN calculating the volumes
    calculate_volume(artifacts)

    # THEN the sample udfs should be set to the correct values
    artifact_1.qc_flag = qc_flag
    artifact_1.udf["Final Volume (uL)"] = final_volume
    artifact_1.udf["Volume H2O (ul)"] = water_volume
    artifact_1.udf["Volume of sample (ul)"] = sample_volume


@pytest.mark.parametrize(
    "sample_concentration",
    [
        3.99,
    ],
)
def test_calculate_volume_exception(
    sample_concentration,
    artifact_1: Artifact,
    caplog,
):
    # GIVEN a sample with a sample concentration that is below the required final concentration
    server("flat_tests")
    artifact_1.udf["Concentration"] = sample_concentration
    artifacts = [artifact_1]

    # WHEN calculating the volumes
    with pytest.raises(Exception) as error_message:
        calculate_volume(artifacts)

    # THEN an Exception should be raised
    assert "Too low or missing concentration" in caplog.text
    assert "MAF volume calculations failed for" in error_message.value.message
