import logging
import sys

import click
from genologics.entities import Process
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts


def org_well_to_sample(
    artifacts: list,
    sample_udfs: list
) -> None:
    """Function to copy artifact udf location and set to sample level.

    For each artifact in the artifacts list, copying the location and set
    sample udf 'Original Well' and 'Original Container' to all samples 
    related to the artifact. 

    Arguments:
        artifacts: list of artifacts to copy from
        sample_udfs: List of sample udfs or udf to set on sample level."""
    
    failed_udfs = 0
    passed_udfs = 0

    for artifact in artifacts:
        sample = artifact.samples[0]

        if artifact.parent_process:
            sys.exit('This is not the first step for these samples. Can therefor not get the original container.')

        if len(artifact.samples)!=1:
            sys.exit('Error: more than one sample per artifact. Unable to copy udfs. Assumes a 1-1 relation between sample and artifact.')

        for sample in artifact.samples:
            for udf in sample_udfs:
                try:
                    if udf == 'Original Well':
                        sample.udf['Original Well'] = artifact.location[1]
                    
                    elif udf == 'Original Container':
                        sample.udf[udf] = artifact.location[0].name
                    
                    sample.put()
                    passed_udfs += 1
                except:
                    failed_udfs += 1               

    if failed_udfs:
        raise MissingUDFsError(
            message=f"The udf {sample_udfs[0]} or {sample_udfs[1]} is missing for {failed_udfs} artifacts. Udfs were set on {passed_udfs} samples."
        )


@click.command()
@options.sample_udfs(help="Sample udfs to set")
@options.input(
    help="Use this flag if you want copy udfs from input artifacts. Defaulte is output artifacts."
)
@click.pass_context
def orgwell_to_sample(ctx, sample_udfs, input):
    """Script to copy artifact udf to sample udf"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input)
        org_well_to_sample(
            artifacts,
            sample_udfs
            )
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
