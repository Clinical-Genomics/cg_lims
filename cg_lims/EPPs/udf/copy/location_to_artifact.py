import logging
import sys
import click

from typing import List, Optional

from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def copy_location_to_artifact(
    artifacts: List,
    location_udfs: List[str]
) -> None:
    """Function to copy artifact location and set to artifact UDF level.

    For each artifact in the artifacts list, copy the location and set
    it for UDFs specified by the user.

    Arguments:
        artifacts: list of artifacts to copy location to
        location_udfs: list of two UDFs to store location information"""

    failed = 0
    passed = 0
    for artifact in artifacts:
        try:
            artifact.udf[location_udfs[0]] = artifact.location[1]
            artifact.udf[location_udfs[1]] = artifact.location[0].name
            artifact.put()
            passed += 1
        except:
            LOG.error(f"Error: Sample {artifact.id} is missing location information."
                     f" Can therefore not set UDF values.")
            failed += 1
    if failed:
        raise InvalidValueError(
            message=f"Failed to set {location_udfs[0]} and {location_udfs[1]} for "
                    f"{failed} artifacts. UDFs were set on {passed} samples."
        )


@click.command()
@options.input(
    help="Use this flag if you want copy location from input artifacts. Default is output artifacts."
)
@options.source_artifact_udfs(
    help="The name of the UDFs that you want to copy to, first from location well and second from location name."
)
@click.pass_context
def location_to_artifact(ctx, input, source_artifact_udfs: Optional[List[str]]):
    """Script to copy location to artifact udf"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input)
        copy_location_to_artifact(
            artifacts=artifacts,
            location_udfs=source_artifact_udfs,
            )
        message = "UDFs have been set on all samples."
        LOG.info(message)
        click.echo("UDFs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
