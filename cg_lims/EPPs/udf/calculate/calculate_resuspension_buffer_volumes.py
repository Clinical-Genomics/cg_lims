"""
CLI module to calculate the resuspension buffer volume (RB Volume) based on the amount of DNA
needed, as specified in the step `Aliquot Samples for Covaris`

For an explanation of the RB volume calculation, see AM-documents 1057, 1464 and 1717
"""

import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import InvalidValueError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

TOTAL_VOLUME_TRUSEQ = 55
TOTAL_VOLUME_LUCIGEN = 25
AMOUNT_NEEDED_TRUSEQ = 1100
AMOUNT_NEEDED_LUCIGEN = 200


def get_concentration(artifact: Artifact) -> float:
    """Get the concentration from the udf"""
    return artifact.udf.get("Concentration")


def get_amount_needed(artifact: Artifact) -> int:
    """Get the amount needed from the udf"""
    return artifact.udf.get("Amount needed (ng)")


def calculate_rb_volume(artifacts: List[Artifact]):
    """Calculate the RB volumes for all samples"""
    invalid_values = 0
    missing_udfs = 0
    for artifact in artifacts:
        concentration = get_concentration(artifact)
        amount_needed = get_amount_needed(artifact)
        if concentration is None or amount_needed is None:
            LOG.error(
                f"Sample {artifact.samples[0].name} is missing udf 'Concentration' or 'Amount "
                f"needed (ng)'."
            )
            missing_udfs += 1
            continue
        sample_volume = amount_needed / concentration
        if amount_needed == AMOUNT_NEEDED_TRUSEQ:
            artifact.udf["RB Volume (ul)"] = TOTAL_VOLUME_TRUSEQ - sample_volume
        elif amount_needed == AMOUNT_NEEDED_LUCIGEN:
            artifact.udf["RB Volume (ul)"] = TOTAL_VOLUME_LUCIGEN - sample_volume
        else:
            LOG.error(
                f"Sample {artifact.samples[0].name}: 'Amount Needed' can only be 200 or 1100."
            )
            invalid_values += 1
            continue
        artifact.udf["Sample Volume (ul)"] = sample_volume
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(
            f"Could not apply calculation for {missing_udfs} out of {len(artifacts)} sample(s): "
            f"Concentration' and 'Amount Needed (ng)' must both be set!"
        )
    if invalid_values:
        raise InvalidValueError(
            f"Could not apply calculation for {invalid_values} out of {len(artifacts)} sample(s): "
            f"'Amount Needed (ng)' value was invalid! Please select the correct amount."
        )


@click.command()
@click.pass_context
def calculate_resuspension_buffer_volume(context: click.Context):
    """Calculate RB volumes based on the amount of DNA needed"""
    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_rb_volume(artifacts=artifacts)
        message = "RB volumes have been calculated!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
