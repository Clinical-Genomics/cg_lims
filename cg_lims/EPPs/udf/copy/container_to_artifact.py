import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte
from genologics.entities import Artifact, Process
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_well_position(artifact: Artifact) -> str:
    """Return the well position of the artifact from its container."""
    return artifact.location[1]


def get_container_name(artifact: Artifact) -> str:
    """Return the name of the container which holds the given artifact."""
    return artifact.container.name


def set_well_udf(destination_artifact: Artifact, source_artifact: Artifact, udf_name: str) -> None:
    """Set the source artifact well position to a UDF on the destination artifact."""
    well = get_well_position(artifact=source_artifact)
    destination_artifact.udf[udf_name] = well
    destination_artifact.put()


def set_container_name_udf(
    destination_artifact: Artifact, source_artifact: Artifact, udf_name: str
) -> None:
    """Set the source artifact container name to a UDF on the destination artifact."""
    container_name = get_container_name(artifact=source_artifact)
    destination_artifact.udf[udf_name] = container_name
    destination_artifact.put()


@click.command()
@options.process_types(
    help="The process type names from where you want to copy the container values."
)
@options.sample_artifact(
    help="Use this flag if you want to copy values from the original container."
)
@options.well_udf(help="The UDF name of where you want to save the source container well position.")
@options.container_name_udf(help="The UDF name of where you want to save the source container name")
@options.measurement(help="UDFs will be set on measurements on the current step. Use in QC-steps.")
@options.input(help="UDFs will be set on input artifacts. Use in the QC-Aggregation-steps")
@click.pass_context
def container_to_artifact(
    ctx,
    process_types: List[str],
    sample_artifact: bool,
    well_udf: str,
    container_name_udf: str,
    measurement: bool,
    input: bool,
):
    """Script to copy well position and/or container name from another process the sample has gone through."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]

    try:
        destination_artifacts: List[Artifact] = get_artifacts(
            process=process, input=input, measurement=measurement
        )
        for destination_artifact in destination_artifacts:
            source_artifact: Artifact = get_latest_analyte(
                lims=lims,
                sample_id=destination_artifact.samples[0].id,
                process_types=process_types,
                sample_artifact=sample_artifact,
            )
            if well_udf:
                set_well_udf(
                    destination_artifact=destination_artifact,
                    source_artifact=source_artifact,
                    udf_name=well_udf,
                )
            if container_name_udf:
                set_container_name_udf(
                    destination_artifact=destination_artifact,
                    source_artifact=source_artifact,
                    udf_name=container_name_udf,
                )
        click.echo("UDFs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
