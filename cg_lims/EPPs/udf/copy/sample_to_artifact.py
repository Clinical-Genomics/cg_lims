#!/usr/bin/env python
from cg_lims.exceptions import LimsError, MissingUDFsError

from cg_lims.get.artifacts import get_artifacts
from cg_lims import options

import logging
import click
import sys

LOG = logging.getLogger(__name__)


def udf_copy_sample_to_artifact(
        artifacts: list, sample_udf: str, art_udf: str) -> None:
    """Function to copy sample udf to artifact.

    For each artifact in the artifacts list, picking the first sample in the art.samples list.
    copying the samp_udf from the sample to the art_udf on the artifact.
    Warns if sample_udf is missing on a sample.
    Logs if a the sample list of a artifact contains more than one sample.


    Arguments:
        artifacts: list of artifacts to copy from
        art_udf: artifact udf to get
        sample_udf: sample udf to set"""

    failed_udfs = 0
    passed_udfs = 0
    for art in artifacts:
        if len(art.samples) > 1:
            LOG.info("More than one sample per artifact, picking the first one")
        sample = art.samples[0]
        udf = sample.udf.get(sample_udf)
        if udf is None:
            failed_udfs += 1
            LOG.error(f"Udf: {sample_udf} missing on sample {sample.id}")
            continue
        art.udf[art_udf] = udf
        art.put()
        LOG.info(f"copied udf {sample_udf} from sample {sample.id} to artifact: {art.id}, udf: {art_udf}")
        passed_udfs += 1

    if failed_udfs:
        raise MissingUDFsError(
            message=f"The udf '{sample_udf}' is missing for {failed_udfs} samples. Udfs were set on {passed_udfs} artifacts."
        )


@click.command()
@options.sample_udf(help="Sample udf to set.")
@options.artifact_udf(help="Artifact udf to get.")
@click.pass_context
def sample_to_artifact(ctx, sample_udf, artifact_udf):
    """Script to copy artifact udf to sample udf"""

    process = ctx.obj["process"]
    try:
        artifacts = get_artifacts(process=process, input=False)
        udf_copy_sample_to_artifact(artifacts, sample_udf, artifact_udf)
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
