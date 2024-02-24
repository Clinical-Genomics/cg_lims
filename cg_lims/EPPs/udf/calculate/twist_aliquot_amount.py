import logging
import sys
from typing import List

import click
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.udfs import get_maximum_amount
from genologics.entities import Artifact

LOG = logging.getLogger(__name__)


# The maximum amount taken into the prep is MAXIMUM_SAMPLE_AMOUNT.
# Any amount below this can be used in the prep if the total amount is limited.
MAXIMUM_SAMPLE_AMOUNT = 250


def get_possible_input_amount(artifact: Artifact) -> float:
    """Return the maximum input amount possible for a sample, depending on the total volume required."""
    process = artifact.parent_process
    sample_volume = artifact.udf.get("Volume (ul)")
    total_volume = process.udf.get("Total Volume (ul)")
    max_volume = min(sample_volume, total_volume)
    concentration = artifact.udf.get("Concentration")
    return max_volume * concentration


def get_maximum_input_for_aliquot(artifact: Artifact) -> float:
    """Return the maximum allowed input amount for the specified artifact."""
    possible_input_amount = get_possible_input_amount(artifact=artifact)
    max_input_amount = get_maximum_amount(artifact=artifact, default_amount=MAXIMUM_SAMPLE_AMOUNT)
    return min(possible_input_amount, max_input_amount)


def set_amount_needed(artifacts: List[Artifact]):
    """The maximum amount taken into the prep is decided by calculating the minimum between MAXIMUM_SAMPLE_AMOUNT and
    <the sample concentration> * <the total volume>.

    Any amount below this can be used in the prep if the total amount or sample volume is limited.
    """

    missing_udfs = 0
    for artifact in artifacts:
        if not artifact.udf.get("Concentration") or not artifact.udf.get("Volume (ul)"):
            missing_udfs += 1
            continue
        maximum_amount = get_maximum_input_for_aliquot(artifact=artifact)
        artifact.udf["Amount needed (ng)"] = maximum_amount
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(f"UDF missing for {missing_udfs} samples")


@click.command()
@click.pass_context
def twist_aliquot_amount(ctx):
    """Calculates amount needed for samples."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=False)
        set_amount_needed(artifacts)
        message = "Amount needed has been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
