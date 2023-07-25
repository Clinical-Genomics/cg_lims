from typing import List
from genologics.entities import Artifact
from genologics.lims import Lims

from cg_lims.get.artifacts import get_latest_analyte
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.set.udfs import copy_udf_process_to_artifact

import logging
import sys
import click

LOG = logging.getLogger(__name__)


def copy_udf_to_artifacts(
    artifacts: List[Artifact],
    process_types: List[str],
    lims: Lims,
    artifact_udf: str,
    process_udf: str,
):
    """Looping over all artifacts. Getting the latest artifact to copy from. Copying."""

    failed_artifacts = 0
    for destination_artifact in artifacts:
        try:
            sample = destination_artifact.samples[0]
            source_artifact: Artifact = get_latest_analyte(
                lims=lims, sample_id=sample.id, process_types=process_types
            )
            source_process = source_artifact.parent_process
            copy_udf_process_to_artifact(
                artifact_udf=artifact_udf,
                process_udf=process_udf,
                artifact=destination_artifact,
                process=source_process,
            )
        except:
            failed_artifacts += 1
    if failed_artifacts:
        raise MissingUDFsError(
            message=f"Failed to set artifact udfs on {failed_artifacts} artifacts. See log for details"
        )


@click.command()
@options.process_types()
@options.artifact_udf()
@options.process_udf()
@options.measurement(help="Udfs will be set on measurements.")
@options.input(help="Udfs will be set on input artifacts.")
@click.pass_context
def process_to_artifact(
    ctx,
    artifact_udf: str,
    process_udf: str,
    measurement: bool,
    input: bool,
    process_types: List[str],
):
    """Script to copy udf to destination artifacts in the current step,
    from process udf defined by process_types and process_udf

    The input and measurement arguments define what kind of artifacts from the current step that
    should be the destination artifacts.
    """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_artifacts(process=process, input=input, measurement=measurement)
        copy_udf_to_artifacts(
            artifacts=artifacts,
            artifact_udf=artifact_udf,
            process_udf=process_udf,
            process_types=process_types,
            lims=lims,
        )
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
