from email.encoders import encode_quopri
import logging
import sys
import click

from typing import List
from genologics.entities import Process, Artifact
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

def org_well_to_sample(
    artifacts: list
) -> None:
    """Function to copy artifact udf location and set to sample level.

    For each artifact in the artifacts list, copying the location and set
    sample udf 'Original Well' and 'Original Container' to all samples 
    related to the artifact. 

    Arguments:
        artifacts: list of artifacts to copy from"""

    failed_udfs = 0
    passed_udfs = 0
    for artifact in artifacts:
        if artifact.parent_process == None and len(artifact.samples) == 1:
            for sample in artifact.samples:
                try:
                    sample.udf['Original Well'] = artifact.location[1]
                    sample.udf['Original Container'] = artifact.location[0].name
                    sample.put()
                    passed_udfs += 1
                except:
                    failed_udfs += 1    
        else:
            if artifact.parent_process:
                click.echo("HI3")
                LOG.error(
                    f"Error: Not the first step for sample {artifact.id}. Can therefor not get the original container."
                )
            elif len(artifact.samples)!=1:
                click.echo("HI4")
                LOG.error(
                    f"Error: more than one sample per artifact for {artifact.id}. Assumes a 1-1 relation between sample and artifact."
                )
            else:
                LOG.error(
                    f"Error: unknown error for {artifact.id}."
                )
    if failed_udfs:
        raise MissingUDFsError(
            message=f"The udf 'Original Well' or 'Original Container' is missing for {failed_udfs} artifacts. Udfs were set on {passed_udfs} samples."
        )


@click.command()
@options.input(
    help="Use this flag if you want copy udfs from input artifacts. Defaulte is output artifacts."
)
@click.pass_context
def orgwell_to_sample(ctx, input):
    """Script to copy artifact udf to sample udf"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input)
        org_well_to_sample(
            artifacts
            )
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
