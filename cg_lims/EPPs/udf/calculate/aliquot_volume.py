import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def calculate_volumes(
    artifacts: List[Artifact],
    process: Process,
    concentration_udf: str,
    sample_volume_udf: str,
    buffer_volume_udf: str,
    total_volume_udf: str,
    amount_needed_udf: str,
):
    """Calculates volumes for diluting samples. The total volume differ depending on
    type of sample. It is given by the process udf <total_volume_udf>."""

    max_volume = process.udf.get(total_volume_udf)
    if not max_volume:
        raise MissingUDFsError(f"Process udf missing:{total_volume_udf}")

    missing_udfs = 0

    for art in artifacts:
        concentration = art.udf.get(concentration_udf)
        amount = art.udf.get(amount_needed_udf)
        if not amount or not concentration:
            missing_udfs += 1
            continue

        art.udf[sample_volume_udf] = amount / float(concentration)
        art.udf[buffer_volume_udf] = max_volume - art.udf[sample_volume_udf]
        art.put()

    if missing_udfs:
        raise MissingUDFsError(
            f"UDFs '{concentration_udf}' and/or '{amount_needed_udf}' missing for {missing_udfs} samples"
        )


@click.command()
@options.concentration_udf(help="Name of the concentration (ng/ul) artifact UDF")
@options.volume_udf(help="Name of the sample volume artifact UDF")
@options.buffer_udf(help="Name of the buffer volume artifact UDF")
@options.total_volume_udf(help="Name of the total volume process UDF")
@options.amount_ng_udf(
    help="Use if you want to overwrite the default UDF name 'Amount needed (ng)'"
)
@options.measurement(
    help="UDFs will be calculated and set on measurement artifacts. Use in QC steps."
)
@options.input(
    help="UDFs will be calculated ans set on input artifacts. Use non-output generating steps."
)
@click.pass_context
def aliquot_volume(
    ctx: click.Context,
    concentration_udf: str,
    volume_udf: str,
    buffer_udf: str,
    total_volume_udf: str,
    amount_ng_udf: str = "Amount needed (ng)",
    measurement: bool = False,
    input: bool = False,
):
    """Calculates amount needed for samples."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=input, measurement=measurement)
        calculate_volumes(
            artifacts=artifacts,
            process=process,
            concentration_udf=concentration_udf,
            sample_volume_udf=volume_udf,
            buffer_volume_udf=buffer_udf,
            total_volume_udf=total_volume_udf,
            amount_needed_udf=amount_ng_udf,
        )
        message = "Volumes have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
