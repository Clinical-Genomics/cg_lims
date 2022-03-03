import pytest
from genologics.entities import Artifact

from cg_lims.EPPs.udf.calculate.calculate_resuspension_buffer_volumes import (
    calculate_rb_volume,
)
from cg_lims.exceptions import InvalidValueError, MissingUDFsError


def test_calculate_rb_volume_missing_concentration(artifact_1: Artifact):
    # GIVEN a list of artifacts with one artifact missing the udf 'Concentration'
    del artifact_1.udf["Concentration"]
    artifacts = [artifact_1]

    # WHEN calculating the rb volumes for all samples
    with pytest.raises(MissingUDFsError) as error_message:
        calculate_rb_volume(artifacts)

    # THEN the MissingUDFsError exception should be raised
    assert (
        f"Could not apply calculation for 1 out of 1 sample(s): 'Concentration' is missing!"
        in error_message.value.message
    )


@pytest.mark.parametrize(
    "concentration",
    [
        100,
    ],
)
def test_calculate_rb_volume_amount_needed_missing(concentration, artifact_1: Artifact):
    # GIVEN a list of artifacts with one artifact having no 'Amount Needed (ng)' udf
    artifact_1.udf["Concentration"] = concentration
    artifacts = [artifact_1]

    # WHEN calculating the rb volumes for all samples
    with pytest.raises(InvalidValueError) as error_message:
        calculate_rb_volume(artifacts)

    # THEN the InvalidValueError exception should be raised
    assert (
        f"'Amount needed (ng)' missing or incorrect for one or more samples."
        in error_message.value.message
    )


@pytest.mark.parametrize(
    "concentration, amount_needed",
    [
        (100, 9001),
    ],
)
def test_calculate_rb_volume_invalid_amount_needed(
    concentration, amount_needed, artifact_1: Artifact
):
    # GIVEN a list of artifacts with one artifact having an invalid 'Amount Needed (ng)' udf
    artifact_1.udf["Concentration"] = concentration
    artifact_1.udf["Amount needed (ng)"] = amount_needed
    artifacts = [artifact_1]

    # WHEN calculating the rb volumes for all samples
    with pytest.raises(InvalidValueError) as error_message:
        calculate_rb_volume(artifacts)

    # THEN the InvalidValueError exception should be raised
    assert (
        f"'Amount needed (ng)' missing or incorrect for one or more samples."
        in error_message.value.message
    )


@pytest.mark.parametrize(
    "concentration, amount_needed, expected_rb_volume, expected_sample_volume",
    [
        (100, 200, 23.0, 2.0),
        (100, 1100, 44.0, 11.0),
    ],
)
def test_calculate_rb_volume_(
    artifact_1: Artifact,
    concentration,
    amount_needed,
    expected_rb_volume,
    expected_sample_volume,
):
    # GIVEN a list of artifacts with one artifact
    artifact_1.udf["Concentration"] = concentration
    artifact_1.udf["Amount needed (ng)"] = amount_needed
    artifacts = [artifact_1]

    # WHEN calculating the rb volumes for all samples
    calculate_rb_volume(artifacts)

    # THEN the correct volumes should be set on the artifact
    assert artifact_1.udf["RB Volume (ul)"] == expected_rb_volume
    assert artifact_1.udf["Sample Volume (ul)"] == expected_sample_volume
