import mock
import pytest
from genologics.entities import Artifact

from cg_lims.EPPs.udf.calculate.calculate_resuspension_buffer_volumes import (
    AMOUNT_NEEDED_LUCIGEN,
    AMOUNT_NEEDED_TRUSEQ,
    VALID_AMOUNTS_NEEDED,
    calculate_sample_rb_volume,
    pre_check_amount_needed_filled_correctly,
)
from cg_lims.exceptions import InvalidValueError


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


@pytest.mark.parametrize(
    "sample_volume, total_volume, expected_return_value",
    [
        (3.6666666666666665, 55, 51.333333333333336),
        (7.990933922240948, 55, 47.00906607775905),
    ],
)
def test_calculate_sample_rb_volume(sample_volume, total_volume, expected_return_value):
    # GIVEN a calculated sample volume and a total_volume

    # WHEN calculating the RB volume
    result = calculate_sample_rb_volume(sample_volume, total_volume)

    # THEN the correct value should be returned
    assert result == expected_return_value
