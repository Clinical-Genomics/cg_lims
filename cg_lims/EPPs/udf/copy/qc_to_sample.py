import logging
import sys

import click
from genologics.entities import Process
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts


def artifacts_to_sample(
    artifacts: list, sample_qc_udf: str = None
) -> None:

    """Function to copy artifact qc flag to sample level.

    For each artifact in the artifacts list, copying the qc_flagg
    to all samples related to the artifact. If a art is a pool, art.samples
    is a list with many samples. Otherwiese a list with only one sample.

    Arguments:
        artifacts: list of artifacts to copy from
        sample_qc_udf: sample qc udf to set based on artifact qc_flag"""

    failed_udfs = 0
    passed_udfs = 0
    for art in artifacts:
        udf = art.qc_flag
        if udf is not None:
            for sample in art.samples:
                if art.qc_flag == "PASSED":
                    sample.udf[sample_qc_udf] = "True"
                else :
                    sample.udf[sample_qc_udf] = "False"
                sample.put()
                passed_udfs += 1  
        else:
            failed_udfs += 1
    if failed_udfs:
        raise MissingUDFsError(
            message=f"The qc_flag was is missing for {failed_udfs} artifacts. Udfs were set on {passed_udfs} samples."
        )            

@click.command()
@options.sample_qc_udf(help="Name of sample QC udf to set.")
@options.input(
    help="Use this flag if you want copy udfs from input artifacts. Defaulte is output artifacts."
)
@click.pass_context
def qc_to_sample(ctx, input,sample_qc_udf):
    """Script to copy artifact QC-flag to sample"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input)
        artifacts_to_sample(
            artifacts=artifacts,
            sample_qc_udf=sample_qc_udf
            )
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
