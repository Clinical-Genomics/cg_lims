
from genologics.entities import Artifact, Process

import logging
import sys
import click
from typing import List

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts


LOG = logging.getLogger(__name__)


def calculate_volumes(artifacts: List[Artifact], process: Process):
    """Calculates volumes for diluting samples. The total volume differ depending on 
    type of sample. It is given by the process udf 'Total Volume (ul)'."""

    max_volume = process.udf.get('Total Volume (ul)')
    if not max_volume:
        raise MissingUDFsError('Process udf missing: Total Volume (ul)')

    missing_udfs = 0

    for art in artifacts:
        concentration = art.udf.get('Concentration')
        amount = art.udf.get('Amount needed (ng)')
        if not amount or not concentration:
            missing_udfs += 1
            continue

        art.udf['Sample Volume (ul)'] = amount/float(concentration)
        art.udf['Volume H2O (ul)'] = max_volume - art.udf['Sample Volume (ul)']
        art.put()

    if missing_udfs:
        raise MissingUDFsError(f"Udf missing for {missing_udfs} samples")


@click.command()
@click.pass_context
def twist_aliquot_volume(ctx):
    """Calculates amount needed for samples."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=False)
        calculate_volumes(artifacts=artifacts, process=process)
        message = "Volumes have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
