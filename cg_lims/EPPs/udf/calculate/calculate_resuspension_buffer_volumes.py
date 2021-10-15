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
from cg_lims.get.fields import get_amount_needed, get_concentration

LOG = logging.getLogger(__name__)

AMOUNT_NEEDED_LUCIGEN = 200
AMOUNT_NEEDED_TRUSEQ = 1100
TOTAL_VOLUME_TRUSEQ = 55
TOTAL_VOLUME_LUCIGEN = 25
VALID_AMOUNTS_NEEDED = [AMOUNT_NEEDED_LUCIGEN, AMOUNT_NEEDED_TRUSEQ]


def pre_check_amount_needed_filled_correctly(artifacts):
    """Checks if amount needed is set correctly. Raises an exception if not"""
    amount_needed_all_samples = [get_amount_needed(artifact) for artifact in artifacts]
    if not all(amount in VALID_AMOUNTS_NEEDED for amount in amount_needed_all_samples):
        raise InvalidValueError(
            f"'Amount needed (ng)' missing or incorrect value for one or more samples. Value can "
            f"only be {', '.join(map(str, VALID_AMOUNTS_NEEDED))}. Please correct and try again."
        )


def calculate_lucigen_rb_volume(sample_volume: float) -> float:
    """calculates the RB volume for Lucigen samples"""
    return TOTAL_VOLUME_LUCIGEN - sample_volume


def calculate_truseq_rb_volume(sample_volume: float) -> float:
    """calculates the RB volume for TruSeq samples"""
    return TOTAL_VOLUME_TRUSEQ - sample_volume


def calculate_rb_volume(artifacts: List[Artifact]):
    """Calculate the RB volumes for all samples"""
    missing_udfs = 0
    for artifact in artifacts:
        concentration = get_concentration(artifact)
        amount_needed = get_amount_needed(artifact)
        if concentration is None:
            LOG.error(
                f"Sample {artifact.samples[0].name} is missing udf 'Concentration'."
            )
            missing_udfs += 1
            continue
        sample_volume = amount_needed / concentration
        volume_calculation_functions = {
            AMOUNT_NEEDED_LUCIGEN: calculate_lucigen_rb_volume,
            AMOUNT_NEEDED_TRUSEQ: calculate_truseq_rb_volume,
        }
        artifact.udf["RB Volume (ul)"] = volume_calculation_functions[amount_needed](
            sample_volume
        )
        artifact.udf["Sample Volume (ul)"] = sample_volume
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(
            f"Could not apply calculation for {missing_udfs} out of {len(artifacts)} sample(s): "
            f"'Concentration' is missing!"
        )


@click.command()
@click.pass_context
def calculate_resuspension_buffer_volume(context: click.Context):
    """Calculate RB volumes based on the amount of DNA needed"""
    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        pre_check_amount_needed_filled_correctly(artifacts)
        calculate_rb_volume(artifacts=artifacts)
        message = "RB volumes have been calculated!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
