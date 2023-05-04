#!/usr/bin/env python
from cg_lims.get.udfs import get_udf_type

import logging
import sys

import click

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def udf_copy_sample_to_artifact(artifacts: list, sample_udf: str, art_udf: str, lims, ignore_fail: bool = False) -> None:
    """Function to copy sample UDF to artifact.

    For each artifact in the artifacts list, picking the first sample in the art.samples list.
    copying the samp_udf from the sample to the art_udf on the artifact.
    Warns if sample_udf is missing on a sample.
    Logs if a the sample list of a artifact contains more than one sample.


    Arguments:
        artifacts: list of artifacts to copy from
        art_udf: artifact UDF to get
        sample_udf: sample UDF to set
        ignore_fail: option to ignore warnings"""
    failed_udfs = 0
    passed_udfs = 0
    udf_type = get_udf_type(lims=lims, udf_name=art_udf, attach_to_name=artifacts[0].output_type)
    for art in artifacts:
        if len(art.samples) > 1:
            LOG.info("More than one sample per artifact, picking the first one")
        sample = art.samples[0]
        udf = sample.udf.get(sample_udf)
        if not isinstance(udf, udf_type):
            try:
                udf = udf_type(udf)
            except:
                failed_udfs += 1
                LOG.error(
                    f"UDF: {sample_udf} missing on sample {sample.id} or it could not be converted to type {udf_type}"
                )
                continue

        art.udf[art_udf] = udf
        art.put()
        LOG.info(
            f"copied UDF {sample_udf} from sample {sample.id} to artifact: {art.id}, UDF: {art_udf}"
        )
        passed_udfs += 1

    if failed_udfs and ignore_fail is False:
        raise MissingUDFsError(
            message=f"The UDF '{sample_udf}' is missing for {failed_udfs} samples. UDFs were set on {passed_udfs} artifacts."
        )


@click.command()
@options.sample_udf(help="Sample UDF to set.")
@options.artifact_udf(help="Artifact UDF to get.")
@options.measurement(help="UDFs will be set on measurements.")
@options.input(help="UDFs will be set on input artifacts.")
@options.ignore_fail(help="Script will not raise exception errors when not all UDFs are set.")
@click.pass_context
def sample_to_artifact(ctx, sample_udf, artifact_udf, measurement, input, ignore_fail):
    """Script to copy sample UDF value to an artifact UDF field."""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_artifacts(process=process, input=input, measurement=measurement)
        udf_copy_sample_to_artifact(artifacts=artifacts, sample_udf=sample_udf, art_udf=artifact_udf, lims=lims, ignore_fail=ignore_fail)
        click.echo("UDFs have been set on all possible samples.")
    except LimsError as e:
        sys.exit(e.message)
