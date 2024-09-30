import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.udfs import get_maximum_amount
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_possible_input_amount(
    artifact: Artifact, sample_volume_udf: str, total_volume_udf: str, concentration_udf: str
) -> float:
    """Return the maximum input amount possible for a sample, depending on the total volume required."""
    process: Process = artifact.parent_process
    sample_volume: float = artifact.udf.get(sample_volume_udf)
    total_volume: float = process.udf.get(total_volume_udf)
    max_volume: float = min(sample_volume, total_volume)
    concentration: float = artifact.udf.get(concentration_udf)
    return max_volume * concentration


def get_maximum_input_for_aliquot(
    artifact: Artifact,
    sample_volume_udf: str,
    total_volume_udf: str,
    concentration_udf: str,
    maximum_sample_amount: float,
) -> float:
    """Return the maximum allowed input amount for the specified artifact."""
    possible_input_amount: float = get_possible_input_amount(
        artifact=artifact,
        sample_volume_udf=sample_volume_udf,
        total_volume_udf=total_volume_udf,
        concentration_udf=concentration_udf,
    )
    max_input_amount: float = get_maximum_amount(
        artifact=artifact, default_amount=maximum_sample_amount
    )
    return min(possible_input_amount, max_input_amount)


def set_amount_needed(
    artifacts: List[Artifact],
    sample_volume_udf: str,
    total_volume_udf: str,
    concentration_udf: str,
    amount_udf: str,
    maximum_sample_amount: float,
) -> None:
    """The maximum amount taken into the prep is decided by calculating the minimum between maximum_sample_amount and
    <the sample concentration> * <the total volume>.

    Any amount below this can be used in the prep if the total amount or sample volume is limited.
    """

    missing_udfs: int = 0
    for artifact in artifacts:
        if not artifact.udf.get(concentration_udf) or not artifact.udf.get(sample_volume_udf):
            missing_udfs += 1
            continue
        maximum_amount: float = get_maximum_input_for_aliquot(
            artifact=artifact,
            sample_volume_udf=sample_volume_udf,
            total_volume_udf=total_volume_udf,
            concentration_udf=concentration_udf,
            maximum_sample_amount=maximum_sample_amount,
        )
        artifact.udf[amount_udf] = maximum_amount
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(f"UDF missing for {missing_udfs} samples")


@click.command()
@options.volume_udf(help="Sample volume artifact UDF name.")
@options.total_volume_udf(help="Total volume process UDF name.")
@options.concentration_udf(help="Sample concentration artifact UDF name.")
@options.amount_ng_udf(help="Sample amount (ng) artifact UDF name.")
@options.maximum_amount(help="The maximum input amount of the prep.")
@click.pass_context
def twist_aliquot_amount(
    ctx,
    volume_udf: str,
    total_volume_udf: str,
    concentration_udf: str,
    amount_udf: str,
    maximum_amount: float,
):
    """Calculates amount needed for samples."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        set_amount_needed(
            artifacts=artifacts,
            sample_volume_udf=volume_udf,
            total_volume_udf=total_volume_udf,
            concentration_udf=concentration_udf,
            amount_udf=amount_udf,
            maximum_sample_amount=maximum_amount,
        )
        message = "Amount needed has been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
