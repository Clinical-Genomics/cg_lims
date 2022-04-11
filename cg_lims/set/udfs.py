from typing import List, Tuple, Iterator

from genologics.entities import Artifact, Process

import logging

from cg_lims.exceptions import MissingUDFsError

LOG = logging.getLogger(__name__)


def copy_artifact_to_artifact(
    destination_artifact: Artifact,
    source_artifact: Artifact,
    artifact_udfs: List[Tuple[str, str]],
    qc_flag: bool = False,
    keep_failed_flags: bool = False,
) -> None:
    """Copying artifact udfs from source artifact to destination artifact.
    Will also copy qc_flag if set to True
    Logging missing uds. Raising MissingUDFsError if any udf is missing"""

    missing_udfs = 0
    artifacts_to_put = False
    for source_udf, destination_udf in artifact_udfs:
        if source_artifact.udf.get(source_udf) is None:
            message = f"Artifact udf {source_udf} missing on artifact {source_artifact.id}"
            LOG.error(message)
            missing_udfs += 1
            continue
        destination_artifact.udf[destination_udf] = source_artifact.udf[source_udf]
        artifacts_to_put = True

    if qc_flag:
        if keep_failed_flags and destination_artifact.qc_flag == "FAILED":
            message = f"QC for destination artifact {destination_artifact.id} is failed, " \
                      f"flag not copied over from source artifact {source_artifact.id}"
            LOG.error(message)
        else:
            destination_artifact.qc_flag = source_artifact.qc_flag
            artifacts_to_put = True

    if artifacts_to_put:
        destination_artifact.put()
    if missing_udfs:
        raise MissingUDFsError(f"Some UDFs missing on the source artifact: {source_artifact.id}")


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
