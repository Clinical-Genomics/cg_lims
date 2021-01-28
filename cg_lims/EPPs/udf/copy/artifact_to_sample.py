#!/usr/bin/env python
import logging
import sys

import click
from genologics.entities import Process
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts


def udf_copy_artifact_to_sample(
    artifacts: list, sample_udf: str, art_udf: str, sample_qc_udf: str = None
) -> None:
    """Function to copy artifact udf and qc to sample level.

    For each artifact in the artifacts list, copying the art_udf and qc_flagg
    to all samples related to the artifact. If a art is a pool, art.samples
    is a list with many samples. Otherwiese a list with only one sample.

    Arguments:
        artifacts: list of artifacts to copy from
        art_udf: artifact udf to get
        sample_udf: sample udf to set
        sample_qc_udf: sample qc udf to set based on artifact qc_flagg"""

    failed_udfs = 0
    passed_udfs = 0
    for art in artifacts:
        udf = art.udf.get(art_udf)
        if udf is not None:
            for sample in art.samples:
                sample.udf[sample_udf] = udf
                if sample_qc_udf:
                    if art.qc_flag == "PASSED":
                        sample.udf[sample_qc_udf] = "True"
                    else:
                        sample.udf[sample_qc_udf] = "False"
                sample.put()
                passed_udfs += 1
        else:
            failed_udfs += 1

    if failed_udfs:
        raise MissingUDFsError(
            message=f"The udf '{art_udf}' is missing for {failed_udfs} artifacts. Udfs were set on {passed_udfs} samples."
        )


@click.command()
@options.sample_udf(help="Sample udf to set.")
@options.artifact_udf(help="Artifact udf to get.")
@options.sample_qc_udf()
@options.input(
    help="Use this flag if you want copy udfs from input artifacts. Defaulte is output artifacts."
)
@click.pass_context
def artifact_to_sample(ctx, sample_udf, artifact_udf, input, sample_qc_udf):
    """Script to copy artifact udf to sample udf"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=input)
        udf_copy_artifact_to_sample(artifacts, sample_udf, artifact_udf, sample_qc_udf)
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
