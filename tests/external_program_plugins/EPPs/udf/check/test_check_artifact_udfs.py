from tests.conftest import server
import logging

from genologics.entities import Artifact

import pytest

from cg_lims.EPPs.udf.check.check_artifact_udfs import check_udfs
from cg_lims.exceptions import MissingUDFsError


def test_check_udfs_missing_udfs(lims):
    # GIVEN:
    server("flat_tests")

    artifacts = [Artifact(lims, id="1"), Artifact(lims, id="2")]
    artifact_udfs = ["Amount taken (ng)", "PCR Plate"]

    # WHEN running check_udfs
    # THEN Missing udfs error is raised
    with pytest.raises(MissingUDFsError):
        check_udfs(artifacts=artifacts, artifact_udfs=artifact_udfs)


def test_check_udfs(caplog, lims):
    # GIVEN:
    server("flat_tests")

    artifact_1 = Artifact(lims, id="1")
    artifact_2 = Artifact(lims, id="2")
    artifact_1.udf["Amount taken (ng)"] = 15
    artifact_1.udf["PCR Plate"] = "some plate"
    artifact_2.udf["Amount taken (ng)"] = 15
    artifact_2.udf["PCR Plate"] = "some plate"
    artifact_2.put()
    artifact_1.put()
    artifacts = [artifact_1, artifact_2]
    artifact_udfs = ["Amount taken (ng)", "PCR Plate"]

    # WHEN running check_udfs
    with caplog.at_level(logging.INFO):
        check_udfs(artifacts=artifacts, artifact_udfs=artifact_udfs)
        # THEN no error is being raised and logging id informing that artifacts were set
        assert "Artifact udfs were all set" in caplog.text
