"""Unit tests for cg_lims.EPPs.udf.calculate.calculate_microbial_aliquot_volumes"""

import pytest
from genologics.entities import Artifact
from pydantic import ValidationError

from cg_lims.EPPs.udf.calculate.calculate_microbial_aliquot_volumes import (
    QC_FAILED,
    QC_PASSED,
    MicrobialAliquotVolumes,
    calculate_volume,
)


@pytest.mark.parametrize(
    "sample_concentration, sample_volume, total_volume, buffer_volume, qc_flag",
    [
        (0, 15, 15, 0, QC_PASSED),
        (1.999, 15, 15, 0, QC_PASSED),
        (2, 15, 15, 0, QC_PASSED),
        (2.001, 15, 15, 0, QC_PASSED),
        (2.30769, 15, 15, 0, QC_PASSED),
        (30 / 13, 15, 15, 0, QC_PASSED),
        (2.30770, 12.99995666681111, 15, 2.0000433331888896, QC_PASSED),
        (7.449, 4.027386226339106, 15, 10.972613773660894, QC_PASSED),
        (7.5, 4, 15, 11, QC_PASSED),
        (7.5001, 4, 15.0002, 11.0002, QC_PASSED),
        (59.999, 4, 119.998, 115.998, QC_PASSED),
        (60, 4, 120, 116, QC_PASSED),
        (60.001, None, None, None, QC_FAILED),
    ],
)
def test_microbial_aliquot_volumes_model(
    sample_concentration,
    sample_volume,
    total_volume,
    buffer_volume,
    qc_flag,
    artifact_1,
):
    # GIVEN a pydantic model for microbial aliquot volumes
    artifact_name = "TEST1"

    # WHEN calculating the volumes in the validators with valid values for 'sample_concentration'
    result = MicrobialAliquotVolumes(
        sample_concentration=sample_concentration, artifact_name=artifact_name
    )

    # THEN the correct results should be set
    assert result.sample_concentration == sample_concentration
    assert result.sample_volume == sample_volume
    assert result.total_volume == total_volume
    assert result.buffer_volume == buffer_volume
    assert result.qc_flag == qc_flag


@pytest.mark.parametrize(
    "sample_concentration",
    [
        None,
    ],
)
def test_maf_volume_model_sample_concentration_validation_error(sample_concentration):
    # GIVEN a pydantic model for Microbial Aliquot volumes
    artifact_name = "TEST1"

    # WHEN calculating the volumes in the validator when there is no 'sample_concentration'
    with pytest.raises(ValidationError) as error_message:
        MicrobialAliquotVolumes(
            sample_concentration=sample_concentration, artifact_name=artifact_name
        )

    # THEN pydantic should raise an exception
    assert error_message.value.errors()[0]["loc"][0] == "sample_concentration"
    assert error_message.value.errors()[0]["type"] == "value_error"
    assert (
        error_message.value.errors()[0]["msg"] == "Concentration udf missing on sample"
    )


@pytest.mark.parametrize(
    "name, sample_concentration, sample_volume, total_volume, buffer_volume, qc_flag",
    [
        ("regular_artifact", 60.001, None, None, None, QC_FAILED),
    ],
)
def test_calculate_volume_regular_sample(
    name,
    sample_concentration,
    sample_volume,
    total_volume,
    buffer_volume,
    qc_flag,
    artifact_1: Artifact,
):
    # GIVEN a sample with a valid sample concentration:
    artifact_1.udf["Concentration"] = sample_concentration
    artifact_1.samples[0].name = name
    artifacts = [artifact_1]

    # WHEN calculating the volumes
    calculate_volume(artifacts)

    # THEN the sample udfs should be set to the correct values
    assert artifact_1.qc_flag == qc_flag
    assert artifact_1.udf.get("Total Volume (uL)") == total_volume
    assert artifact_1.udf.get("Volume Buffer (ul)") == buffer_volume
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume


@pytest.mark.parametrize(
    "name, sample_concentration, sample_volume, total_volume, buffer_volume, qc_flag",
    [
        ("NTC-CG99", 60.001, 0, 15, 15, QC_PASSED),
    ],
)
def test_calculate_volume_ntc_artifact(
    name,
    sample_concentration,
    sample_volume,
    total_volume,
    buffer_volume,
    qc_flag,
    artifact_1: Artifact,
):
    # GIVEN a sample with a valid sample concentration:
    artifact_1.udf["Concentration"] = sample_concentration
    artifact_1.samples[0].name = name
    artifacts = [artifact_1]

    # WHEN calculating the volumes
    calculate_volume(artifacts)

    # THEN the sample udfs should be set to the correct values
    assert artifact_1.qc_flag == qc_flag
    assert artifact_1.udf.get("Total Volume (uL)") == total_volume
    assert artifact_1.udf.get("Volume Buffer (ul)") == buffer_volume
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume


@pytest.mark.parametrize(
    "name, sample_concentration",
    [
        ("regular_artifact", None),
    ],
)
def test_calculate_volume_exception(
    name,
    sample_concentration,
    artifact_1: Artifact,
    caplog,
):
    # GIVEN a sample missing the sample concentration udf
    del artifact_1.udf["Concentration"]
    artifact_1.samples[0].name = "regular_artifact"
    artifacts = [artifact_1]

    # WHEN calculating the volumes
    with pytest.raises(Exception) as error_message:
        calculate_volume(artifacts)

    # THEN an Exception should be raised
    assert "Concentration udf missing on sample" in caplog.text
    assert (
        "Microbial aliquot volume calculations failed for"
        in error_message.value.message
    )
