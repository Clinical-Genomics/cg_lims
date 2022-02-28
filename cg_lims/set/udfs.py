from typing import List

from genologics.entities import Artifact, Process

import logging

from cg_lims.exceptions import MissingUDFsError

LOG = logging.getLogger(__name__)


def copy_udf(
    destination_artifact: Artifact, source_artifact: Artifact, artifact_udfs: List[str]
) -> None:
    """Copying artifact udfs from source artifact to destination artifact.
    Logging missing uds without raising error"""

    artifacts_to_put = False

    for udf in artifact_udfs:
        if not source_artifact.udf.get(udf):
            message = f"artifact udf {udf} missing on artifact {source_artifact.id}"
            LOG.error(message)
            continue
        destination_artifact.udf[udf] = source_artifact.udf[udf]
        artifacts_to_put = True

    if artifacts_to_put:
        destination_artifact.put()


def copy_udf_process_to_artifact(
    artifact: Artifact, process: Process, artifact_udf: str, process_udf: str
) -> None:
    """Copying process udf to artifact udf.
    Logging and raising missing uds error"""

    if not process.udf.get(process_udf):
        message = f"process: {process.id} missing udf {process_udf}"
        LOG.error(message)
        raise MissingUDFsError(message=message)
    try:
        artifact.udf[artifact_udf] = process.udf[process_udf]
        artifact.put()
    except:
        message = f"{artifact_udf} doesn't seem to be a valid artifact udf."
        LOG.error(message)
        raise MissingUDFsError(message=message)
