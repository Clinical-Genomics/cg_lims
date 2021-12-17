"""Unit tests for cg_lims.EPPs.udf.calculate.calculate_microbial_aliquot_volumes"""

import pytest
from genologics.entities import Artifact

from cg_lims.EPPs.udf.calculate.calculate_microbial_aliquot_volumes import (
    calculate_volumes,
)
from cg_lims.exceptions import HighConcentrationError, MissingUDFsError


@pytest.mark.parametrize(
    "sample_concentration, sample_volume, total_volume, buffer_volume",
    [
        (0, 15, 15, 0),
        (1.999, 15, 15, 0),
        (2, 15, 15, 0),
        (2.001, 15, 15, 0),
        (2.30769, 15, 15, 0),
        (30 / 13, 15, 15, 0),
        (2.30770, 12.99995666681111, 15, 2.0000433331888896),
        (7.449, 4.027386226339106, 15, 10.972613773660894),
        (7.5, 4, 15, 11),
        (7.5001, 4, 15.0002, 11.0002),
        (59.999, 4, 119.998, 115.998),
        (60, 4, 120, 116),
    ],
)
def test_calculate_microbial_aliquot_volumes(
    sample_concentration: float,
    sample_volume: float,
    total_volume: float,
    buffer_volume: float,
    artifact_1: Artifact,
):
    # GIVEN a sample with a valid concentration
    artifact_1.udf["Concentration"] = sample_concentration
    artifacts = [artifact_1]

    # WHEN calculating the microbial aliquot volumes
    calculate_volumes(artifacts=artifacts)

    # THEN the sample udfs should be set to the correct values
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume
    assert artifact_1.udf.get("Volume Buffer (ul)") == buffer_volume
    assert artifact_1.udf.get("Total Volume (uL)") == total_volume


@pytest.mark.parametrize(
    "sample_concentration",
    [
        None,
    ],
)
def test_calculate_microbial_aliquot_volumes_concentration_missing(
    sample_concentration: float, artifact_1: Artifact, caplog
):
    # GIVEN a sample with no concentration udf
    artifact_1.udf["Concentration"] = sample_concentration
    artifacts = [artifact_1]

    # WHEN calculating the microbial aliquot volumes
    with pytest.raises(MissingUDFsError) as error_message:
        calculate_volumes(artifacts=artifacts)

    # THEN a MissingUDFsError should be raised
    assert (
        "Could not apply calculations for 1 out of 1 sample(s): 'Concentration' is missing!"
        in error_message.value.message
    )


@pytest.mark.parametrize(
    "sample_concentration",
    [
        60.001,
    ],
)
def test_calculate_microbial_aliquot_volumes_concentration_too_high(
    sample_concentration: float, artifact_1: Artifact, caplog
):
    # GIVEN a sample with a concentration value greater than the maximum allowed
    artifact_1.udf["Concentration"] = sample_concentration
    artifacts = [artifact_1]

    # WHEN calculating the microbial aliquot volumes
    with pytest.raises(HighConcentrationError) as error_message:
        calculate_volumes(artifacts=artifacts)

    # THEN a HighConcentrationError should be raised
    assert (
        "Could not apply calculations for one or more sample(s): concentration too high!"
        in error_message.value.message
    )


@pytest.mark.parametrize(
    "sample_concentration, sample_volume, total_volume, buffer_volume, name",
    [
        (999, 0, 15, 15, "NTC-CG99"),
    ],
)
def test_calculate_microbial_aliquot_volumes_ntc_sample(
    sample_concentration: float,
    sample_volume: float,
    total_volume: float,
    buffer_volume: float,
    name: str,
    artifact_1: Artifact,
):
    # GIVEN an NTC sample with a valid concentration
    artifact_1.udf["Concentration"] = sample_concentration
    artifact_1.samples[0].name = name
    artifacts = [artifact_1]

    # WHEN calculating the microbial aliquot volumes
    calculate_volumes(artifacts=artifacts)

    # THEN the sample udfs should be set to the correct values
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume
    assert artifact_1.udf.get("Volume Buffer (ul)") == buffer_volume
    assert artifact_1.udf.get("Total Volume (uL)") == total_volume
