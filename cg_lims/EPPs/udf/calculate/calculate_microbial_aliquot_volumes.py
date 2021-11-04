"""
CLI module to calculate the resuspension buffer volume (RB Volume) based on the amount of DNA
needed, as specified in the step `CG002 - Normalization of microbial samples for sequencing`
"""
import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def calculate_volume(artifacts: List[Artifact]) -> None:
    """Determines the total volume, water volume, and sample volume"""
    pass


@click.command()
@click.pass_context
def calculate_microbial_aliquot_volumes(context: click.Context):
    """Calculate microbial aliquot volumes based on the Concentration udf"""
    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_volume(artifacts=artifacts)
        message = "Microbial aliquot volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
