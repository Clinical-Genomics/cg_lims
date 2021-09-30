"""CLI module to calculate dilution volumes from Concentration udf"""
import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts

FINAL_CONCENTRATION = 4
LOG = logging.getLogger(__name__)
LOWEST_POSSIBLE_CONCENTRATION = 4
MINIMUM_FINAL_VOLUME = 15
QC_FAILED = "FAILED"
QC_PASSED = "PASSED"
SAMPLE_CONCENTRATION_1 = 20
SAMPLE_CONCENTRATION_2 = 244
SAMPLE_CONCENTRATION_3 = 364
SAMPLE_CONCENTRATION_4 = 724
SAMPLE_CONCENTRATION_5 = 1444
SAMPLE_VOLUME_1 = 3.0
SAMPLE_VOLUME_2 = 2.0
SAMPLE_VOLUME_3 = 1.0
SAMPLE_VOLUME_4 = 0.5


def get_sample_concentration(artifact: Artifact) -> float:
    """Returns the value of the concentration udf"""
    return artifact.udf.get("Concentration")


def calculate_final_volume(sample_volume: float, sample_concentration: float) -> float:
    """Calculates the final volume for a sample"""
    return sample_volume * sample_concentration / FINAL_CONCENTRATION


def calculate_sample_volume(sample_concentration: float) -> float:
    """Calculates the sample volume"""
    return MINIMUM_FINAL_VOLUME * FINAL_CONCENTRATION / sample_concentration


def calculate_volume(artifacts: List[Artifact]) -> None:
    """Determines the final volume, water volume, and sample volume"""
    failed_artifacts = []

    for artifact in artifacts:
        qc_flag = QC_FAILED
        sample_concentration = get_sample_concentration(artifact)
        if (
            sample_concentration is None
            or sample_concentration < LOWEST_POSSIBLE_CONCENTRATION
        ):
            LOG.warning(
                f"Sample concentration too low or missing for sample {artifact}."
            )
            failed_artifacts.append(artifact)
            continue
        if sample_concentration < SAMPLE_CONCENTRATION_1:
            sample_volume = calculate_sample_volume(sample_concentration)
        elif sample_concentration < SAMPLE_CONCENTRATION_2:
            sample_volume = SAMPLE_VOLUME_1
            qc_flag = QC_PASSED
        elif sample_concentration < SAMPLE_CONCENTRATION_3:
            sample_volume = SAMPLE_VOLUME_2
        elif sample_concentration < SAMPLE_CONCENTRATION_4:
            sample_volume = SAMPLE_VOLUME_3
        elif sample_concentration < SAMPLE_CONCENTRATION_5:
            sample_volume = SAMPLE_VOLUME_4
        else:
            LOG.warning(f"Could not calculate sample volume for {artifact}.")
            failed_artifacts.append(artifact)
            continue

        final_volume = calculate_final_volume(sample_volume, sample_concentration)

        if final_volume < MINIMUM_FINAL_VOLUME:
            LOG.warning(
                f"The final calculated volume is smaller than the minimum final volume for sample {artifact}"
            )
            failed_artifacts.append(artifact)
            continue

        artifact.qc_flag = qc_flag
        artifact.udf["Final Volume (uL)"] = final_volume
        artifact.udf["Volume H2O (ul)"] = final_volume - sample_volume
        artifact.udf["Volume of sample (ul)"] = sample_volume
        artifact.put()

    if failed_artifacts:
        raise LimsError(
            f"MAF volume calculations failed for {failed_artifacts}, out of {len(artifacts)} artifact(s)."
        )


@click.command()
@click.pass_context
def maf_calculate_volume(context: click.Context):
    """Calculate dilution volumes based on the Concentration udf"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")

    process = context.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_volume(artifacts=artifacts)
        message = "MAF volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
