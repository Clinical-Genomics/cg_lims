from typing import List, Optional, Tuple, Iterator
from genologics.entities import Artifact
from genologics.lims import Lims

from cg_lims.get.artifacts import get_latest_analyte
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError, ArgumentError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.set.udfs import copy_artifact_to_artifact

import logging
import sys
import click

LOG = logging.getLogger(__name__)


def copy_udfs_to_all_artifacts(
    artifacts: List[Artifact],
    process_types: List[str],
    lims: Lims,
    udfs: List[Tuple[str, str]],
    sample_artifact: bool = False,
    qc_flag: bool = False,
):
    """Looping over all artifacts. Getting the latest artifact to copy from. Copying."""

    failed_artifacts = 0
    for destination_artifact in artifacts:
        try:
            sample = destination_artifact.samples[0]
            source_artifact = get_latest_analyte(
                lims=lims,
                sample_id=sample.id,
                process_types=process_types,
                sample_artifact=sample_artifact,
            )
            copy_artifact_to_artifact(
                destination_artifact=destination_artifact,
                source_artifact=source_artifact,
                artifact_udfs=udfs,
                qc_flag=qc_flag,
            )
        except:
            failed_artifacts += 1
    if failed_artifacts:
        raise MissingUDFsError(
            message=f"Failed to set artifact udfs on {failed_artifacts} artifacts. See log for details"
        )


@click.command()
@options.process_types(help="The process type names from where you want to copy the artifact udf.")
@options.sample_artifact(help="Use this flag if you want to copy udf from original artifact")
@options.artifact_udfs(
    help="The name of the udf that you want to set (Will be used also for source artifact udf if "
    "that option has not been set.)"
)
@options.source_artifact_udfs(
    help="The name of the udf that you want to copy. Not required. Use if the name of the "
    "source udf is not the ame as the destination udf."
)
@options.measurement(help="Udfs will be set on measurements on the current step. Use in QC-steps.")
@options.input(help="Udfs will be set on input artifacts. Use in the QC-Aggregation-steps")
@options.qc_flag()
@click.pass_context
def artifact_to_artifact(
    ctx,
    artifact_udfs: List[str],
    source_artifact_udfs: Optional[List[str]],
    measurement: bool,
    input: bool,
    process_types: List[str],
    sample_artifact: bool,
    qc_flag: bool,
):
    """Script to copy udfs to destination artifacts in the current step, from source artifacts
    generated by steps defined by process_types, or from the original sample artifact if the sample-artifact
     flagg is true.

    The input and measurement arguments define what kind of artifacts from the current step that
    should be the destination artifacts.
    """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    if not source_artifact_udfs:
        source_artifact_udfs = artifact_udfs
    if len(source_artifact_udfs) != len(artifact_udfs):
        raise ArgumentError(
            "The number of artifact-udfs and source-artifact-udfs must be the same."
        )

    udf_pairs = zip(source_artifact_udfs, artifact_udfs)
    try:
        artifacts = get_artifacts(process=process, input=input, measurement=measurement)
        copy_udfs_to_all_artifacts(
            artifacts=artifacts,
            udfs=list(udf_pairs),
            process_types=process_types,
            lims=lims,
            sample_artifact=sample_artifact,
            qc_flag=qc_flag,
        )
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
