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
    source_artifact_udfs :  List[str]
) -> None:
    """Function to copy artifact udf location and set to artifact level.

    For each artifact in the artifacts list, copying the location and set
    sample udf 'Original Well' and 'Original Container' to all samples 
    related to the artifact. 

    Arguments:
        artifacts: list of artifacts to copy from"""

    failed = 0
    passed = 0
    for artifact in artifacts:        

        try:
            artifact.udf[source_artifact_udfs[0]] = artifact.location[1]
            artifact.udf[source_artifact_udfs[1]] = artifact.location[0].name
            artifact.put()
            passed += 1
        except:
            LOG.error(
                f"Error: Sample {artifact.id} missing udf location. Can therefor not assign values."
        )
            failed += 1

    if failed:
        raise InvalidValueError(
            message=f"Failed to set 'Original Well' and 'Original Container' for {failed} artifacts. Udfs were set on {passed} samples."
        )

@click.command()
@options.input(
    help="Use this flag if you want copy udfs from input artifacts. Default is output artifacts."
)
@options.source_artifact_udfs(
    help="The name of the udf that you want to copy, like 'Library plate name' and 'Library plate well'"
)
@click.pass_context
def location_to_artifact(ctx, input, source_artifact_udfs: Optional[List[str]] ):
    """Script to copy artifact udf to sample udf"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input)
        copy_location_to_artifact(
            artifacts,
            source_artifact_udfs,
            )
        message = "Udfs have been set on all samples."
        LOG.info(message)
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)

