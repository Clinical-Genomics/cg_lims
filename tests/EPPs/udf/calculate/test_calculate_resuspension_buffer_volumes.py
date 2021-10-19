import mock
import pytest
from genologics.entities import Artifact

from cg_lims.EPPs.udf.calculate.calculate_resuspension_buffer_volumes import (
    AMOUNT_NEEDED_LUCIGEN,
    AMOUNT_NEEDED_TRUSEQ,
    VALID_AMOUNTS_NEEDED,
    calculate_rb_volume,
    pre_check_amount_needed_filled_correctly,
)
from cg_lims.exceptions import InvalidValueError, MissingUDFsError


def test_pre_check_amount_needed_filled_correctly(
    artifact_1: Artifact, artifact_2: Artifact
):
    # GIVEN a list of artifacts with udf 'Amount needed (ng)` set correctly
    artifact_1.udf["Amount needed (ng)"] = AMOUNT_NEEDED_TRUSEQ
    artifact_2.udf["Amount needed (ng)"] = AMOUNT_NEEDED_LUCIGEN
    artifacts = [artifact_1, artifact_2]

    # WHEN checking the udfs
    result = pre_check_amount_needed_filled_correctly(artifacts)

    # THEN no exception should be raised
    assert result is None


def test_pre_check_amount_needed_filled_incorrectly(
    artifact_1: Artifact, artifact_2: Artifact
):
    # GIVEN a list of artifacts with udf 'Amount needed (ng)` set incorrectly
    artifact_2.udf["Amount needed (ng)"] = 100
    artifacts = [artifact_1, artifact_2]

    # WHEN checking the udfs
    with pytest.raises(InvalidValueError) as error_message:
        pre_check_amount_needed_filled_correctly(artifacts)

    # THEN an exception should be raised
    assert (
        f"'Amount needed (ng)' missing or incorrect value for one or more samples. Value can only "
        f"be {', '.join(map(str, VALID_AMOUNTS_NEEDED))}. Please correct and try again."
        in error_message.value.message
    )


def test_calculate_rb_volume_missing_concentration(artifact_1: Artifact):
    # GIVEN a list of artifacts with one artifact missing the udf 'Concentration'
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
