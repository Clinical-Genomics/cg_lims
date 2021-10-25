import pytest
from genologics.entities import Artifact

from cg_lims.EPPs.udf.calculate.calculate_water_volume_rna import (
    calculate_sample_and_water_volumes,
)
from cg_lims.exceptions import InvalidValueError, MissingUDFsError


def test_calculate_water_volume_rna_missing_concentration(artifact_1: Artifact):
    # GIVEN a list of artifacts with one artifact missing the udf 'Concentration'
    del artifact_1.udf["Concentration"]
    artifacts = [artifact_1]

    # WHEN calculating the sample and water volumes for all samples
    with pytest.raises(MissingUDFsError) as error_message:
        calculate_sample_and_water_volumes(artifacts)

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
def test_calculate_water_volume_rna_amount_needed_missing(
    concentration, artifact_1: Artifact
):
    # GIVEN a list of artifacts with one artifact having no 'Amount Needed (ng)' udf
    artifact_1.udf["Concentration"] = concentration
    del artifact_1.udf["Amount needed (ng)"]
    artifacts = [artifact_1]

    # WHEN calculating sample and water volumes for all samples
    with pytest.raises(InvalidValueError) as error_message:
        calculate_sample_and_water_volumes(artifacts)

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
def test_calculate_water_volume_rna_(
    concentration, amount_needed, artifact_1: Artifact
):
    # GIVEN a list of artifacts with one artifact having an invalid 'Amount Needed (ng)' udf
    artifact_1.udf["Concentration"] = concentration
    artifact_1.udf["Amount needed (ng)"] = amount_needed
    artifacts = [artifact_1]

    # WHEN calculating the sample and water volumes for all samples
    with pytest.raises(InvalidValueError) as error_message:
        calculate_sample_and_water_volumes(artifacts)

    # THEN the InvalidValueError exception should be raised
    assert (
        f"'Amount needed (ng)' missing or incorrect for one or more samples."
        in error_message.value.message
    )


@pytest.mark.parametrize(
    "concentration, amount_needed, expected_water_volume, expected_sample_volume",
    [
        (100, 200, 23.0, 2.0),
        (100, 300, 22.0, 3.0),
        (100, 400, 21.0, 4.0),
        (100, 500, 20.0, 5.0),
    ],
)
def test_calculate_water_volume_rna(
    artifact_1: Artifact,
    concentration,
    amount_needed,
    expected_water_volume,
    expected_sample_volume,
):
    # GIVEN a list of artifacts with one artifact
    artifact_1.udf["Concentration"] = concentration
    artifact_1.udf["Amount needed (ng)"] = amount_needed
    artifacts = [artifact_1]

    # WHEN calculating the sample and water volumes for all samples
    calculate_sample_and_water_volumes(artifacts)

    # THEN the correct volumes should be set on the artifact
    assert artifact_1.udf["Volume H2O (ul)"] == expected_water_volume
    assert artifact_1.udf["Sample Volume (ul)"] == expected_sample_volume
