"""
CLI module to calculate dilution volumes from Concentration udf

For an explanation of the sample volume calculation and setting of the QG flag, see
AM-document 1243 Method - Preparing Plate for Genotyping, section 3.3.2 Preparing the plate
"""

import logging
import sys
from typing import List, Tuple

import click
from genologics.entities import Artifact

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

FINAL_CONCENTRATION = 4
CONCENTRATION_UPPER_LIMIT = 1444
MINIMUM_TOTAL_VOLUME = 15
MAXIMUM_WATER_VOLUME = 180
QC_FAILED = "FAILED"
QC_PASSED = "PASSED"
PIPETTING_VOLUMES = [3, 2, 1, 0.5]


def get_sample_concentration(artifact: Artifact) -> float:
    """Returns the value of the concentration udf"""
    return artifact.udf.get("Concentration")


def calculate_final_volume(sample_volume: float, sample_concentration: float) -> float:
    """Calculates the final volume for a sample"""
    return sample_volume * sample_concentration / FINAL_CONCENTRATION


def calculate_volumes_for_low_concentration_samples(
    sample_concentration: float,
) -> Tuple[float, float, float, str]:
    """Calculates the sample volume. The sample volume is increased to reach the minimum total volume. This
    occurs at lower concentration levels where standard pipetting volumes are not enough to reach the desired final
    concentration and final volume."""
    sample_volume: float = MINIMUM_TOTAL_VOLUME * FINAL_CONCENTRATION / sample_concentration
    final_volume = calculate_final_volume(sample_volume, sample_concentration)
    water_volume = final_volume - sample_volume
    qc_flag = QC_FAILED
    return final_volume, water_volume, sample_volume, qc_flag


def calculate_volumes(sample_concentration: float) -> Tuple[float, float, float, str]:
    """Calculates all volumes (final volume, water volume and sample volume) and sets the QC flag."""
    for sample_volume in PIPETTING_VOLUMES:
        final_volume = sample_concentration * sample_volume / FINAL_CONCENTRATION
        water_volume = final_volume - sample_volume
        if water_volume < MAXIMUM_WATER_VOLUME:
            qc_flag = QC_PASSED if sample_volume == 3 else QC_FAILED
            return final_volume, water_volume, sample_volume, qc_flag


def calculate_volume(artifacts: List[Artifact]) -> None:
    """Determines the final volume, water volume, and sample volume"""
    failed_artifacts = []

    for artifact in artifacts:
        sample_concentration = get_sample_concentration(artifact)
        if sample_concentration is None or sample_concentration < FINAL_CONCENTRATION:
            LOG.warning(
                f"Sample concentration too low or missing for sample {artifact.samples[0].name}."
            )
            failed_artifacts.append(artifact)
            continue
        if sample_concentration >= CONCENTRATION_UPPER_LIMIT:
            LOG.warning(
                f"Sample concentration too high for sample {artifact.samples[0].name}."
            )
            failed_artifacts.append(artifact)
            continue

        if sample_concentration < 20:
            (
                final_volume,
                water_volume,
                sample_volume,
                qc_flag,
            ) = calculate_volumes_for_low_concentration_samples(sample_concentration)
        elif sample_concentration >= 20:
            final_volume, water_volume, sample_volume, qc_flag = calculate_volumes(
                sample_concentration
            )
        else:
            LOG.warning(
                f"Could not calculate sample volume for sample {artifact.samples[0].name}."
            )
            failed_artifacts.append(artifact)
            continue

        artifact.qc_flag = qc_flag
        artifact.udf["Final Volume (uL)"] = final_volume
        artifact.udf["Volume H2O (ul)"] = water_volume
        artifact.udf["Volume of sample (ul)"] = sample_volume
        artifact.put()

    if failed_artifacts:
        raise LimsError(
            f"MAF volume calculations failed for {len(failed_artifacts)} samples, "
            f"{len(artifacts) - len(failed_artifacts)} updates successful. "
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
