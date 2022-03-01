import pytest
from genologics.entities import Artifact

from cg_lims.exceptions import MissingUDFsError
from cg_lims.set.udfs import copy_artifact_to_artifact
from tests.conftest import server


def test_copy_udfs(lims):
    # GIVEN a sample with a udf "Sequencing Analysis"
    server("flat_tests")
    concentration_udf = "Concentration (nM)"
    volume_udf = "Volume (ul)"
    source_artifact = Artifact(lims=lims, id="1")
    destination_artifact = Artifact(lims=lims, id="2")
    source_artifact.udf[concentration_udf] = 2
    source_artifact.udf[volume_udf] = 3
    source_artifact.put()

    # WHEN running copy_udf
    copy_artifact_to_artifact(
        source_artifact=source_artifact,
        destination_artifact=destination_artifact,
        artifact_udfs=[(concentration_udf, concentration_udf), (volume_udf, volume_udf)],
    )

    # THEN the udfs have been set:
    assert destination_artifact.udf[volume_udf] == source_artifact.udf[volume_udf]
    assert destination_artifact.udf[concentration_udf] == source_artifact.udf[concentration_udf]


def test_copy_udfs_missing_udfs(lims, caplog):
    # GIVEN a sample with a udf "Sequencing Analysis"
    server("flat_tests")
    concentration_udf = "Concentration (nM)"
    volume_udf = "Volume (ul)"
    source_artifact = Artifact(lims=lims, id="1")
    source_artifact.udf.clear()
    source_artifact.put()
    destination_artifact = Artifact(lims=lims, id="2")

    # WHEN running copy_udf
    with pytest.raises(MissingUDFsError) as error_message:
        copy_artifact_to_artifact(
            source_artifact=source_artifact,
            destination_artifact=destination_artifact,
            artifact_udfs=[(concentration_udf, concentration_udf), (volume_udf, volume_udf)],
        )

    # THEN the udfs have not been set
    assert destination_artifact.udf.get(volume_udf) is None
    assert destination_artifact.udf.get(concentration_udf) is None
    assert f"Artifact udf {volume_udf} missing on artifact {source_artifact.id}" in caplog.text
    assert (
        f"Artifact udf {concentration_udf} missing on artifact {source_artifact.id}" in caplog.text
    )
