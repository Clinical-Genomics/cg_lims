"""CLI module to calculate the sample and water volume based on the amount of RNA needed,
as specified in the step `Aliquot Samples for Fragmentation (RNA)` """

import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import InvalidValueError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

TOTAL_VOLUME = 25
VALID_AMOUNTS_NEEDED = [200, 300, 400, 500]


def calculate_sample_and_water_volumes(artifacts: List[Artifact]):
    """Calculate the sample and water volumes for all samples"""
    missing_udfs = 0
    for artifact in artifacts:
        concentration = artifact.udf.get("Concentration")
        amount_needed = artifact.udf.get("Amount needed (ng)")
        if concentration is None:
            LOG.error(
                f"Sample {artifact.samples[0].name} is missing udf 'Concentration'."
            )
            missing_udfs += 1
            continue
        if amount_needed not in VALID_AMOUNTS_NEEDED:
            raise InvalidValueError(
                f"'Amount needed (ng)' missing or incorrect for one or more samples. Value can "
                f"only be {', '.join(map(str, VALID_AMOUNTS_NEEDED))}."
            )
        sample_volume = amount_needed / concentration
        artifact.udf["Sample Volume (ul)"] = sample_volume
        artifact.udf["Volume H2O (ul)"] = TOTAL_VOLUME - sample_volume
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(
            f"Could not apply calculation for {missing_udfs} out of {len(artifacts)} sample(s): "
            f"'Concentration' is missing!"
        )


@click.command()
@click.pass_context
def calculate_water_volume_rna(context: click.Context):
    """Calculate sample and water volumes based on the amount of RNA needed"""
    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_sample_and_water_volumes(artifacts=artifacts)
        message = "Sample and H2O volumes have been calculated!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
