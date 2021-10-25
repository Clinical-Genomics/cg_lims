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

AMOUNT_NEEDED_LUCIGEN = 200
AMOUNT_NEEDED_TRUSEQ = 1100
TOTAL_VOLUME_LUCIGEN = 25
TOTAL_VOLUME_TRUSEQ = 55


def calculate_rb_volume(artifacts: List[Artifact]):
    """Calculate the RB volumes for all samples"""
    missing_udfs = 0
    for artifact in artifacts:
        concentration = artifact.udf.get("Concentration")
        amount_needed = artifact.udf.get("Amount needed (ng)")
        if concentration is None:
            LOG.error(
                f"Sample {artifact.id} is missing udf 'Concentration'."
            )
            missing_udfs += 1
            continue
        if amount_needed not in [AMOUNT_NEEDED_LUCIGEN, AMOUNT_NEEDED_TRUSEQ]:
            raise InvalidValueError(
                f"'Amount needed (ng)' missing or incorrect for one or more samples. Value can "
                f"only be {', '.join(map(str, [AMOUNT_NEEDED_LUCIGEN, AMOUNT_NEEDED_TRUSEQ]))}."
            )
        sample_volume = amount_needed / concentration
        if amount_needed == AMOUNT_NEEDED_LUCIGEN:
            artifact.udf["RB Volume (ul)"] = TOTAL_VOLUME_LUCIGEN - sample_volume
        if amount_needed == AMOUNT_NEEDED_TRUSEQ:
            artifact.udf["RB Volume (ul)"] = TOTAL_VOLUME_TRUSEQ - sample_volume
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
        calculate_rb_volume(artifacts=artifacts)
        message = "RB volumes have been calculated!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
