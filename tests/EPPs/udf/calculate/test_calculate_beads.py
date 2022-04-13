import mock
import pytest

from cg_lims.EPPs.udf.calculate.calculate_beads import (
    calculate_beads_volume,
    calculate_elution_volume,
    calculate_volumes,
)
from cg_lims.EPPs.udf.calculate.calculate_water import calculate_water_volume
from cg_lims.exceptions import MissingUDFsError
from genologics.entities import Artifact
from genologics.lims import Lims
from tests.conftest import server


def test_calculate_elution_volume():
    # GIVEN a sample volume
    sample_volume = 30.0

    # WHEN calculating the elution volume
    result = calculate_elution_volume(sample_volume)

    # THEN the elution is 80*sample_volume
    assert result == sample_volume * 0.8
    assert isinstance(result, float)


SAMPLE_VOLUME_LIMIT = 50
OFFSET = 3.0


@pytest.mark.parametrize(
    "sample_volume, expected_return_value",
    [
        (SAMPLE_VOLUME_LIMIT - OFFSET, OFFSET),
        (SAMPLE_VOLUME_LIMIT, 0.0),
        (SAMPLE_VOLUME_LIMIT + OFFSET, 0.0),
    ],
)
def test_calculate_water_volume(sample_volume: float, expected_return_value: float):
    # GIVEN a sample volume less than, equal to, and greater than SAMPLE_VOLUME_LIMIT

    # WHEN calculating the water volume
    result = calculate_water_volume(
        sample_volume=sample_volume, sample_volume_limit=SAMPLE_VOLUME_LIMIT
    )

    # THEN the water volume should be calculated correctly
    assert result == expected_return_value
    assert isinstance(result, float)


def test_calculate_beads_volume():
    # GIVEN a sample_volume
    sample_volume = 50

    # WHEN calculating the beads volume
    result = calculate_beads_volume(sample_volume=sample_volume)

    # THEN calculate beads volume should be twice the sum of the sample volume and water volume
    assert result == sample_volume * 2


@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_elution_volume")
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_beads_volume")
@pytest.mark.parametrize(
    "sample_volume, elution_volume, beads_volume",
    [(20.0, 40.0, 100.0)],
)
def test_calculate_volumes_single_artifact(
    mock_beads_volume,
    mock_elution_volume,
    sample_volume: float,
    elution_volume: float,
    beads_volume: float,
    artifact_1: Artifact,
):
    # GIVEN an artifact with a udf "Sample Volume (ul)"
    server("flat_tests")
    artifact_1.udf["Sample Volume (ul)"] = sample_volume
    artifacts = [artifact_1]
    mock_elution_volume.return_value = elution_volume
    mock_beads_volume.return_value = beads_volume

    # WHEN calculating the volumes
    calculate_volumes(artifacts=artifacts)

    # THEN the calculated volumes for elution, water and beads are correct
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume
    assert artifact_1.udf.get("Volume Elution (ul)") == elution_volume
    assert artifact_1.udf.get("Volume Beads (ul)") == beads_volume


def test_calculate_volumes_single_artifact_missing_sample_volume_udf(
    artifact_1: Artifact,
):
    # GIVEN an artifact with no udf "Sample Volume (ul)"
    server("flat_tests")
    assert artifact_1.udf.get("Sample Volume (ul)") is None
    artifacts = [artifact_1]

    # WHEN calculating the volumes
    # THEN an exception should be raised
    with pytest.raises(MissingUDFsError) as error_message:
        calculate_volumes(artifacts=artifacts)
    assert f"missing for 1 out of 1 samples" in error_message.value.message


@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_elution_volume")
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_water.calculate_water_volume")
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_beads_volume")
@pytest.mark.parametrize(
    "sample_volume, elution_volume, water_volume, beads_volume",
    [(20.0, 40.0, 30.0, 100.0)],
)
def test_calculate_volumes_multiple_artifacts_missing_sample_volume_udf(
    mock_beads_volume,
    mock_water_volume,
    mock_elution_volume,
    sample_volume: float,
    elution_volume: float,
    water_volume: float,
    beads_volume: float,
    lims: Lims,
    artifact_1: Artifact,
    artifact_2: Artifact,
):
    # GIVEN one out of two artifacts has no udf "Sample Volume (ul)"
    server("flat_tests")
    artifact_1.udf["Sample Volume (ul)"] = sample_volume
    assert artifact_1.udf.get("Sample Volume (ul)") is not None
    assert artifact_2.udf.get("Sample Volume (ul)") is None
    artifacts = [artifact_1, artifact_2]

    mock_elution_volume.return_value = elution_volume
    mock_water_volume.return_value = water_volume
    mock_beads_volume.return_value = beads_volume

    # WHEN calculating the volumes
    with pytest.raises(MissingUDFsError) as error_message:
        calculate_volumes(artifacts=artifacts)

    # THEN an exception should be raised
    assert f"missing for 1 out of 2 samples" in error_message.value.message

    # AND the artifact with the udf "Sample Volume (ul) should be processed correctly
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume
    assert artifact_1.udf.get("Volume Elution (ul)") == elution_volume
