
from genologics.entities import Artifact

import logging
import sys
import click
from typing import List

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


# The maximum amount taken into the prep is MAXIMUM_SAMPLE_AMOUNT.
# Any amount below this can be used in the prep if the total amount is limited.
MAXIMUM_SAMPLE_AMOUNT = 250


def set_amount_needed(artifacts: List[Artifact]):
    """The maximum amount taken into the prep is MAXIMUM_SAMPLE_AMOUNT. 
    Any amount below this can be used in the prep if the total amount is limited."""

    missing_udfs = 0
    for art in artifacts:
        amount = art.udf.get('Amount (ng)')
        if not amount:
            missing_udfs += 1
            continue
        if amount >= MAXIMUM_SAMPLE_AMOUNT:
            art.udf['Amount needed (ng)'] = MAXIMUM_SAMPLE_AMOUNT
        else:
            art.udf['Amount needed (ng)'] = amount
        art.put()

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
        message =  "Amount needed has been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
