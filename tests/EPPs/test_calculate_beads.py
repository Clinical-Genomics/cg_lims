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


def test_calculate_elution_volume_less_than_sample_volume_boundary():
    # GIVEN a sample volume smaller than SAMPLE_VOLUME_BOUNDARY (50.0)
    sample_volume = 20.0
    assert sample_volume < SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the elution volume
    result = calculate_elution_volume(sample_volume)

    # THEN the elution volume should be equal to ELUTION_VOLUME (40.0)
    assert result == ELUTION_VOLUME
    assert result == 40.0
    assert isinstance(result, float)


def test_calculate_elution_volume_greater_than_sample_volume_boundary():

    # GIVEN a sample volume larger than SAMPLE_VOLUME_BOUNDARY (50.0)
    sample_volume = 60.0
    assert sample_volume > SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the elution volume
    result = calculate_elution_volume(sample_volume)

    # THEN the elution volume should be equal to ELUTION_VOLUME_FACTOR * sample_volume - 0.8 *
    # 60.0 = 48.0
    assert result == ELUTION_VOLUME_FACTOR * sample_volume
    assert result == 48.0
    assert isinstance(result, float)


def test_calculate_elution_volume_equal_to_sample_volume_boundary():
    # GIVEN a sample volume equal to the SAMPLE_VOLUME_BOUNDARY (50.0)
    sample_volume = 50.0
    assert sample_volume == SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the elution volume
    result = calculate_elution_volume(sample_volume)

    # THEN the elution volume should be equal to ELUTION_VOLUME_FACTOR * sample_volume = 0.8 *
    # 50.0 = 40.0 = ELUTION_VOLUME
    assert result == ELUTION_VOLUME_FACTOR * sample_volume
    assert result == ELUTION_VOLUME
    assert result == 40.0
    assert isinstance(result, float)


def test_calculate_water_volume_less_than_sample_volume_boundary():
    # GIVEN a sample volume smaller than SAMPLE_VOLUME_BOUNDARY (50.0)
    sample_volume = 20.0
    assert sample_volume < SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the water volume
    result = calculate_water_volume(sample_volume)

    # THEN the water volume should be equal to SAMPLE_VOLUME_BOUNDARY - sample_volume = 30.0
    assert result == 30.0
    assert isinstance(result, float)


def test_calculate_water_volume_greater_than_sample_volume_boundary():
    # GIVEN a sample volume larger than SAMPLE_VOLUME_BOUNDARY (50.0)
    sample_volume = 60.0
    assert sample_volume > SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the water volume
    result = calculate_water_volume(sample_volume)

    # THEN the water volume should be equal to 0
    assert result == 0.0
    assert isinstance(result, float)


def test_calculate_water_volume_equal_to_sample_volume_boundary():
    # GIVEN a sample volume equal to SAMPLE_VOLUME_BOUNDARY (50.0)
    sample_volume = 50.0
    assert sample_volume == SAMPLE_VOLUME_BOUNDARY

    # WHEN calculating the water volume
    result = calculate_water_volume(sample_volume)

    # THEN the water volume should be equal to 0
    assert result == 0.0
    assert isinstance(result, float)


def test_calculate_beads_volume():
    # GIVEN a sample_volume and a water volume
    sample_volume = 20.0
    h2o_volume = 30.0

    # WHEN calculating the beads volume
    result = calculate_beads_volume(sample_volume=sample_volume, h2o_volume=h2o_volume)

    # THEN calculate beads volume should be twice the sum of the sample volume and water volume
    assert result == 100.0


@pytest.mark.parametrize(
    "sample_volume,water_volume,result", [(20.0, 30.0, 100.0), (40.0, 100.0, 200.0)]
)
def test_calculate_beads_volume_parametrized(sample_volume, water_volume, result):
    # GIVEN a sample_volume and a water volume
    sample_volume = sample_volume
    h2o_volume = water_volume

    # WHEN calculating the beads volume
    result = calculate_beads_volume(sample_volume=sample_volume, h2o_volume=h2o_volume)

    # THEN calculate beads volume should be twice the sum of the sample volume and water volume
    assert result == result


@pytest.mark.parametrize(
    "sample_volume,elution_volume,water_volume,beads_volume",
    [(20.0, 40.0, 30.0, 100.0)],
)
def test_calculate_volumes_single_artifact(
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

    # WHEN calculating the volumes
    calculate_volumes(artifacts=artifacts)

    # THEN the calculated volumes for elution, water and beads are correct
    assert artifact_1.udf.get("Sample Volume (ul)") == sample_volume
    assert artifact_1.udf.get("Volume Elution (ul)") == elution_volume
    assert artifact_1.udf.get("Volume H2O (ul)") == water_volume
    assert artifact_1.udf.get("Volume beads (ul)") == beads_volume


def test_calculate_volumes_multiple_artifacts(
    artifact_1: Artifact, artifact_2: Artifact
):
    # GIVEN two artifact with a udf "Sample Volume (ul)" with value 20.0 and 60.0 respectively
    server("flat_tests")
    artifact_1.udf["Sample Volume (ul)"] = 20.0
    artifact_2.udf["Sample Volume (ul)"] = 60.0

    artifacts = [artifact_1, artifact_2]

    # WHEN calculating the volumes
    calculate_volumes(artifacts=artifacts)

    # THEN the calculated volumes for elution, water and beads are 40.0, 30.0 and 100.0 for
    # artifact_1 and 48.0, 0.0 and 120.0 for artifact_2
    assert artifact_1.udf.get("Sample Volume (ul)") == 20.0
    assert artifact_1.udf.get("Volume Elution (ul)") == 40.0
    assert artifact_1.udf.get("Volume H2O (ul)") == 30.0
    assert artifact_1.udf.get("Volume beads (ul)") == 100.0
    assert artifact_2.udf.get("Sample Volume (ul)") == 60.0
    assert artifact_2.udf.get("Volume Elution (ul)") == 48.0
    assert artifact_2.udf.get("Volume H2O (ul)") == 0.0
    assert artifact_2.udf.get("Volume beads (ul)") == 120.0


def test_calculate_volumes_single_artifact_missing_sample_volume_udf(
    lims: Lims, artifact_1: Artifact, caplog
):
    # GIVEN an artifact with no udf "Sample Volume (ul)"
    server("flat_tests")
    assert artifact_1.udf.get("Sample Volume (ul)") is None
    artifacts = [artifact_1]

    # WHEN calculating the volumes
    # THEN an exception should be raised
    with pytest.raises(MissingUDFsError) as error_message:
        calculate_volumes(artifacts=artifacts)
    assert (
        f"missing for 1 out of {len(artifacts)} samples" in error_message.value.message
    )


def test_calculate_volumes_multiple_artifacts_missing_sample_volume_udf(
    lims: Lims, artifact_1: Artifact, artifact_2: Artifact
):
    # GIVEN one out of two artifacts has no udf "Sample Volume (ul)"
    server("flat_tests")
    artifact_1.udf["Sample Volume (ul)"] = 20.0
    assert artifact_1.udf.get("Sample Volume (ul)") is not None
    assert artifact_2.udf.get("Sample Volume (ul)") is None
    artifacts = [artifact_1, artifact_2]

    # WHEN calculating the volumes
    with pytest.raises(MissingUDFsError) as error_message:
        calculate_volumes(artifacts=artifacts)

    # THEN an exception should be raised
    assert (
        f"missing for 1 out of {len(artifacts)} samples" in error_message.value.message
    )

    # AND the artifact with the udf "Sample Volume (ul) should be processed correctly
    assert artifact_1.udf.get("Sample Volume (ul)") == 20.0
    assert artifact_1.udf.get("Volume Elution (ul)") == 40.0
    assert artifact_1.udf.get("Volume H2O (ul)") == 30.0
    assert artifact_1.udf.get("Volume beads (ul)") == 100.0
