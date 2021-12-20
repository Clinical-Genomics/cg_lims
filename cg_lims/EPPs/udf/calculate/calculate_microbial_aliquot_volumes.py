"""
CLI module to calculate the resuspension buffer volume (RB Volume) based on the amount of DNA
needed, as specified in the step `CG002 - Normalization of microbial samples for sequencing`

For an explanation of the volume calculations, see AM-document 1764 Method - Manual
cost-efficient library preparation for microbial WGS """
import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import HighConcentrationError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

FINAL_CONCENTRATION = 2
LOG = logging.getLogger(__name__)
MAXIMUM_CONCENTRATION = 60
QC_FAILED = "FAILED"
QC_PASSED = "PASSED"


def calculate_volumes(artifacts: List[Artifact]) -> None:
    """Determines the total volume, water volume, and sample volume"""
    missing_udfs = 0
    high_concentration = False
    qc_flag = QC_PASSED
    for artifact in artifacts:
        concentration = artifact.udf.get("Concentration")
        if concentration is None:
            LOG.error(
                f"Sample {artifact.samples[0].name} is missing udf 'Concentration'."
            )
            missing_udfs += 1
            continue
        if artifact.samples[0].name.startswith("NTC-CG"):
            sample_volume = 0
            buffer_volume = 15
        elif concentration < FINAL_CONCENTRATION:
            sample_volume = 15
            buffer_volume = 0
        elif 2 <= concentration <= 7.5:
            total_volume = 15
            sample_volume = float(FINAL_CONCENTRATION * total_volume) / concentration
            buffer_volume = total_volume - sample_volume
            if buffer_volume < 2:
                sample_volume = 15
                buffer_volume = 0
        elif 7.5 < concentration <= MAXIMUM_CONCENTRATION:
            sample_volume = 4
            total_volume = float(concentration * sample_volume) / FINAL_CONCENTRATION
            buffer_volume = total_volume - sample_volume
        else:
            high_concentration = True
            artifact.qc_flag = QC_FAILED
            artifact.put()
            continue
        artifact.qc_flag = qc_flag
        artifact.udf["Sample Volume (ul)"] = sample_volume
        artifact.udf["Volume Buffer (ul)"] = buffer_volume
        artifact.udf["Total Volume (uL)"] = buffer_volume + sample_volume
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(
            f"Could not apply calculations for {missing_udfs} out of {len(artifacts)} sample(s): "
            f"'Concentration' is missing!"
        )

    if high_concentration:
        mu = "\u03BC"
        raise HighConcentrationError(
            f"Could not apply calculations for one or more sample(s): concentration too high (> "
            f"60 ng/{mu}l)! "
        )


@click.command()
@click.pass_context
def calculate_microbial_aliquot_volumes(context: click.Context):
    """Calculate microbial aliquot volumes based on the Concentration udf"""
    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_volumes(artifacts=artifacts)
        message = "Microbial aliquot volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
