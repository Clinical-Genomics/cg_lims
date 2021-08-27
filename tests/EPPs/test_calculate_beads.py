import mock
import pytest

from cg_lims.EPPs.udf.calculate.calculate_beads import (
    ELUTION_VOLUME,
    ELUTION_VOLUME_FACTOR,
    SAMPLE_VOLUME_BOUNDARY,
    calculate_beads_volume,
    calculate_elution_volume,
    calculate_volumes,
    calculate_water_volume,
)
from cg_lims.exceptions import MissingUDFsError
from genologics.entities import Artifact
from genologics.lims import Lims
from tests.conftest import server

OFFSET = 20


@pytest.mark.parametrize(
    "sample_volume, return_value",
    [
        (SAMPLE_VOLUME_BOUNDARY - OFFSET, ELUTION_VOLUME),
        (SAMPLE_VOLUME_BOUNDARY, ELUTION_VOLUME_FACTOR * SAMPLE_VOLUME_BOUNDARY),
        (
            SAMPLE_VOLUME_BOUNDARY + OFFSET,
            ELUTION_VOLUME_FACTOR * (SAMPLE_VOLUME_BOUNDARY + OFFSET),
        ),
    ],
)
def test_calculate_elution_volume(sample_volume: float, return_value: float):
    # GIVEN a sample volume less than, equal to, and greater than SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the elution volume
    result = calculate_elution_volume(sample_volume)

    # THEN the elution volume should be calculated correctly
    assert result == return_value
    assert isinstance(result, float)


@pytest.mark.parametrize(
    "sample_volume, expected_return_value",
    [
        (SAMPLE_VOLUME_BOUNDARY - OFFSET, OFFSET),
        (SAMPLE_VOLUME_BOUNDARY, 0.0),
        (SAMPLE_VOLUME_BOUNDARY + OFFSET, 0.0),
    ],
)
def test_calculate_water_volume(sample_volume: float, expected_return_value: float):
    # GIVEN a sample volume less than, equal to, and greater than SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the water volume
    result = calculate_water_volume(sample_volume)

    # THEN the water volume should be calculated correctly
    assert result == expected_return_value
    assert isinstance(result, float)


@pytest.mark.parametrize(
    "sample_volume, water_volume, expected_return_value",
    [
        (50.0, 50.0, 200.0),
        (0.0, 50.0, 100.0),
        (50.0, 0.0, 100.0),
    ],
)
def test_calculate_beads_volume(
    sample_volume: float, water_volume: float, expected_return_value: float
):
    # GIVEN a sample_volume and a water_volume

    # WHEN calculating the beads volume
    result = calculate_beads_volume(
        sample_volume=sample_volume, h2o_volume=water_volume
    )

    # THEN calculate beads volume should be twice the sum of the sample volume and water volume
    assert result == expected_return_value
    assert isinstance(result, float)


@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_elution_volume")
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_water_volume")
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_beads_volume")
@pytest.mark.parametrize(
    "sample_volume, elution_volume, water_volume, beads_volume",
    [(20.0, 40.0, 30.0, 100.0)],
)
def test_calculate_volumes_single_artifact(
    mock_beads_volume,
    mock_water_volume,
    mock_elution_volume,
    sample_volume: float,
    elution_volume: float,
    water_volume: float,
    beads_volume: float,
    artifact_1: Artifact,
):
    # GIVEN an artifact with a udf "Sample Volume (ul)"
    server("flat_tests")
    artifact_1.udf["Sample Volume (ul)"] = sample_volume
    artifacts = [artifact_1]
    mock_elution_volume.return_value = elution_volume
    mock_water_volume.return_value = water_volume
    mock_beads_volume.return_value = beads_volume

    # WHEN calculating the volumes
    calculate_volumes(artifacts=artifacts)

    # THEN the calculated volumes for elution, water and beads are correct
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume
    assert artifact_1.udf.get("Volume Elution (ul)") == elution_volume
    assert artifact_1.udf.get("Volume H2O (ul)") == water_volume
    assert artifact_1.udf.get("Volume Beads (ul)") == beads_volume


@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_elution_volume")
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_water_volume")
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_beads_volume")
@pytest.mark.parametrize(
    "sample_volume_1, elution_volume_1, water_volume_1, beads_volume_1,"
    "sample_volume_2, elution_volume_2, water_volume_2, beads_volume_2",
    [(20.0, 40.0, 30.0, 100.0, 60.0, 48.0, 0.0, 120.0)],
)
def test_calculate_volumes_multiple_artifacts(
    mock_beads_volume,
    mock_water_volume,
    mock_elution_volume,
    sample_volume_1: float,
    elution_volume_1: float,
    water_volume_1: float,
    beads_volume_1: float,
    sample_volume_2: float,
    elution_volume_2: float,
    water_volume_2: float,
    beads_volume_2: float,
    artifact_1: Artifact,
    artifact_2: Artifact,
):
    # GIVEN two artifact with a udf "Sample Volume (ul)"
    server("flat_tests")
    artifact_1.udf["Sample Volume (ul)"] = sample_volume_1
    artifact_2.udf["Sample Volume (ul)"] = sample_volume_2

    artifacts = [artifact_1, artifact_2]

    mock_elution_volume.side_effect = [elution_volume_1, elution_volume_2]
    mock_water_volume.side_effect = [water_volume_1, water_volume_2]
    mock_beads_volume.side_effect = [beads_volume_1, beads_volume_2]

    # WHEN calculating the volumes
    calculate_volumes(artifacts=artifacts)

    # THEN the calculated volumes for elution, water and beads should be assigned correctly
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume_1
    assert artifact_1.udf.get("Volume Elution (ul)") == elution_volume_1
    assert artifact_1.udf.get("Volume H2O (ul)") == water_volume_1
    assert artifact_1.udf.get("Volume Beads (ul)") == beads_volume_1
    assert artifact_2.udf.get("Sample Volume (ul)") == sample_volume_2
    assert artifact_2.udf.get("Volume Elution (ul)") == elution_volume_2
    assert artifact_2.udf.get("Volume H2O (ul)") == water_volume_2
    assert artifact_2.udf.get("Volume Beads (ul)") == beads_volume_2


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
@mock.patch("cg_lims.EPPs.udf.calculate.calculate_beads.calculate_water_volume")
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
    assert artifact_1.udf.get("Volume H2O (ul)") == water_volume
