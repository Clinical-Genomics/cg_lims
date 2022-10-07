from typing import List, Tuple
from genologics.entities import Artifact

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.set.udfs import copy_artifact_to_artifact

import logging
import sys
import click

LOG = logging.getLogger(__name__)


def copy_udfs_to_all_analytes(
    measurements: List[Artifact],
    udfs: List[Tuple[str, str]],
):
    """Looping over all analytes and copying over the measurement values for the given UDFs."""

    failed_artifacts = 0
    for measurement in measurements:
        try:
            analyte = measurement.input_artifact_list()[0]
            copy_artifact_to_artifact(
                destination_artifact=analyte,
                source_artifact=measurement,
                artifact_udfs=udfs,
            )
        except:
            failed_artifacts += 1
    if failed_artifacts:
        raise MissingUDFsError(
            message=f"Failed to set artifact udfs on {failed_artifacts} artifacts. See log for details"
        )


@click.command()
@options.artifact_udfs(
    help="The name of the udf that you want to set"
)
@click.pass_context
def measurement_to_analyte(
    ctx,
    artifact_udfs: List[str],
):
    """
    Script to copy UDFs to measurements in the current step, from their source analytes in the same step.
    """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    udfs = list(zip(artifact_udfs, artifact_udfs))

    try:
        measurements = get_artifacts(process=process, measurement=True)
        copy_udfs_to_all_analytes(
            measurements=measurements,
            udfs=udfs,
        )
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
