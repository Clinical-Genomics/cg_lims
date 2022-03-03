"""Scripts to check the process artifact udfs are set.
"""
import logging
import sys
from typing import List
import click
from genologics.entities import Process, Artifact
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def check_udfs(artifacts: List[Artifact], artifact_udfs: List[str]) -> None:
    """Check that process artifact udfs are set."""

    warning = []
    for udf in artifact_udfs:
        missing_udfs = [artifact.id for artifact in artifacts if artifact.udf.get(udf) is None]
        if missing_udfs:
            warning.append(f"Udf: {udf} missing for artifacts: {missing_udfs}.")
    if warning:
        LOG.warning(" ".join(warning))
        raise MissingUDFsError(message=" ".join(warning))
    LOG.info("Artifact udfs were all set.")


@click.command()
@options.artifact_udfs()
@options.measurement(help="Set to True if you want to check measurement udfs.")
@options.input(help="Set to True if you want to check the input artifact udfs.")
@click.pass_context
def check_artifact_udfs(
    ctx: click.Context, artifact_udfs: List[str], input: bool, measurement: bool
):
    """Script to check that artifact udfs are set."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input, measurement=measurement)
        check_udfs(artifacts=artifacts, artifact_udfs=artifact_udfs)
        click.echo("Artifact udfs were checked.")
    except LimsError as e:
        sys.exit(e.message)
