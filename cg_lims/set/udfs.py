from typing import List, Tuple

from genologics.entities import Artifact, Process
from genologics.lims import Lims

import logging

from cg_lims.exceptions import MissingUDFsError
from cg_lims.get.artifacts import get_latest_result_files

LOG = logging.getLogger(__name__)


def copy_artifact_to_artifact(
    destination_artifact: Artifact,
    source_artifact: Artifact,
    artifact_udfs: List[Tuple[str, str]],
    qc_flag: bool = False,
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
        if qc_flag:
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


def aggregate_qc_and_copy_udfs_to_artifacts(
    artifacts: List[Artifact],
    process_types: List[str],
    lims: Lims,
    udfs: List[Tuple[str, str]],
    qc_flag: bool = False,
):
    """Looping over all artifacts. Getting the latest artifact to copy from. Copying."""

    failed_artifacts = 0
    for destination_artifact in artifacts:
        try:
            sample = destination_artifact.samples[0]
            source_artifact = get_latest_result_files(
                lims=lims,
                sample_id=sample.id,
                process_types=process_types,
                output_generation_type="PerInput",
            )
            copy_artifact_to_artifact(
                destination_artifact=destination_artifact,
                source_artifact=source_artifact[0],
                artifact_udfs=udfs,
                qc_flag=(qc_flag and destination_artifact.qc_flag != "FAILED"),
            )

        except:
            failed_artifacts += 1
    if failed_artifacts:
        raise MissingUDFsError(
            message=f"Failed to set artifact udfs on {failed_artifacts} artifacts. See log for details"
        )
