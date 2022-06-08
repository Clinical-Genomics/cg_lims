import logging
import sys
import click

from typing import List
from genologics.entities import Process, Artifact
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

def pool_name_to_sample(
    artifacts: list
) -> None:
    """Function to copy artifact udf location and set to sample level.

    For each artifact in the artifacts list, copying the location and set
    sample udf 'Original Well' and 'Original Container' to all samples 
    related to the artifact. 

    Arguments:
        artifacts: list of artifacts to copy from"""

    failed = 0
    passed = 0
    for artifact in artifacts:

        for sample in artifact.samples:

            try:
                sample.udf['Pool Name'] = artifact.name
                sample.put()
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
@click.pass_context
def pool_to_sample(ctx, input):
    """Script to copy artifact udf to sample udf"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input)
        pool_name_to_sample(
            artifacts
            )
        message = "Udfs have been set on all samples."
        LOG.info(message)
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
