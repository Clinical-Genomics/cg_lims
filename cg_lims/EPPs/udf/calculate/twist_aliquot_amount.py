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


def get_skip_rc_input_amount(artifact: Artifact) -> float:
    """Return the maximum input amount for a sample which has skipped reception control."""
    process = artifact.parent_process
    sample_volume = artifact.udf.get("Volume (ul)")
    total_volume = process.udf.get("Total Volume (ul)")
    max_volume = min(sample_volume, total_volume)
    concentration = artifact.udf.get("Concentration")
    return max_volume * concentration


def get_maximum_input_for_aliquot(artifact: Artifact) -> float:
    """Return the maximum allowed input amount for the specified artifact."""
    if artifact.samples[0].udf.get("Skip Reception Control QC"):
        return get_skip_rc_input_amount(artifact=artifact)
    return get_maximum_amount(artifact=artifact, default_amount=MAXIMUM_SAMPLE_AMOUNT)


def set_amount_needed(artifacts: List[Artifact]):
    """For samples that have skipped RC QC:
    - The maximum amount taken into the prep is decided by calculating <the sample concentration> * <the total volume>.
    For all other samples:
    - The maximum amount is decided by MAXIMUM_SAMPLE_AMOUNT.
    Any amount below this can be used in the prep if the total amount is limited."""

    missing_udfs = 0
    for artifact in artifacts:
        amount = artifact.udf.get("Amount (ng)")
        maximum_amount = get_maximum_input_for_aliquot(artifact=artifact)
        if not amount:
            missing_udfs += 1
            continue
        if amount >= maximum_amount:
            artifact.udf["Amount needed (ng)"] = maximum_amount
        else:
            artifact.udf["Amount needed (ng)"] = amount
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(f"Udf missing for {missing_udfs} samples")


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
