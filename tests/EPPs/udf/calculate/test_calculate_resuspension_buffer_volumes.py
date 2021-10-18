import mock
import pytest
from genologics.entities import Artifact

from cg_lims.EPPs.udf.calculate.calculate_resuspension_buffer_volumes import (
    VALID_AMOUNTS_NEEDED,
    pre_check_amount_needed_filled_correctly,
)
from cg_lims.exceptions import InvalidValueError


def test_pre_check_amount_needed_filled_correctly(
    artifact_1: Artifact, artifact_2: Artifact
):
    # GIVEN a list of artifacts with udf 'Amount needed (ng)` set correctly
    artifact_1.udf["Amount needed (ng)"] = 1100
    artifact_2.udf["Amount needed (ng)"] = 1100
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

    assert (
        f"'Amount needed (ng)' missing or incorrect value for one or more samples. Value can only be 200, 1100. Please correct and try again."
        in error_message.value.message
    )
