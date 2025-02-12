import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingValueError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_artifact_volume(artifact: Artifact, volume_udf: str) -> float:
    """Return the artifact volume."""
    sample_volume: float = artifact.udf[volume_udf]
    return sample_volume


def calculate_total_sample_volume(artifacts: List[Artifact], volume_udf: str) -> float:
    """Return the total volume of all samples in the step."""
    return sum(artifact.udf[volume_udf] for artifact in artifacts)


def calculate_per_sample_mix_volumes(volume_udf: float, ratio: str) -> float:
    """Calculate the volume reagent mix to add per sample."""
    mix_volume: float = float(ratio) * volume_udf
    return mix_volume


def calculate_beads_per_sample(
    volume_udf: float,
    annealing_volume: float,
    polymerase_dilution_volume: float,
) -> float:
    """Set the SMRTbell cleanup bead volume (1X of sample, added annealing mix and polymerase dilution volume)."""
    beads_volume: float = volume_udf + annealing_volume + polymerase_dilution_volume
    return beads_volume


def calculate_total_ABC_volumes(
    factor: str, total_sample_volume: str, reagent_ratio: str = None
) -> float:
    """Calculate the total master mix and reagent volumes needed for all samples in the step.
    Adding some excess represented by factor."""
    if not reagent_ratio:
        reagent_ratio = 1
    return round(float(factor) * total_sample_volume * float(reagent_ratio), 2)


def set_reagent_volumes_per_sample(
    artifact: Artifact,
    annealing_mix_volume: float,
    polymerase_dilution_volume: float,
    beads_volume: float,
    elution_volume: Optional[float],
) -> None:
    """Set reagent mix volumes on artifact level."""
    artifact.udf["Volume Annealing Mix (ul)"] = annealing_mix_volume
    artifact.udf["Volume Polymerase Dilution Mix (ul)"] = polymerase_dilution_volume
    artifact.udf["Volume Cleanup Beads (ul)"] = beads_volume
    if elution_volume:
        artifact.udf["Volume Elution (ul)"] = elution_volume
    artifact.put()


def set_total_ABC_volumes(
    process: Process,
    factor: str,
    total_sample_volume: str,
    annealing_reagent_ratio: str,
    polymerase_buffer_ratio: str,
    polymerase_dilution_mix_ratio: str,
    sequencing_polymerase_ratio: str,
) -> None:
    """Set the total master mix and reagent volumes needed for all samples in the step.
    Adding some excess specified in the cli command."""

    process.udf["Total Annealing Mix Volume (ul)"] = calculate_total_ABC_volumes(
        factor=factor, total_sample_volume=total_sample_volume
    )
    process.udf["Annealing Buffer Volume (ul)"] = calculate_total_ABC_volumes(
        factor=factor,
        total_sample_volume=total_sample_volume,
        reagent_ratio=annealing_reagent_ratio,
    )
    process.udf["Standard Sequencing Primer Volume (ul)"] = calculate_total_ABC_volumes(
        factor=factor,
        total_sample_volume=total_sample_volume,
        reagent_ratio=annealing_reagent_ratio,
    )
    process.udf["Total Polymerase Dilution Mix Volume (ul)"] = calculate_total_ABC_volumes(
        factor=factor,
        total_sample_volume=total_sample_volume,
        reagent_ratio=polymerase_dilution_mix_ratio,
    )
    process.udf["Polymerase Buffer Volume (ul)"] = calculate_total_ABC_volumes(
        factor=factor,
        total_sample_volume=total_sample_volume,
        reagent_ratio=polymerase_buffer_ratio,
    )
    process.udf["Sequencing Polymerase Volume (ul)"] = calculate_total_ABC_volumes(
        factor=factor,
        total_sample_volume=total_sample_volume,
        reagent_ratio=sequencing_polymerase_ratio,
    )
    process.put()


@click.command()
@options.volume_udf()
@options.preset_volume()
@options.factor()
@options.annealing_reagent_ratio()
@options.polymerase_buffer_ratio()
@options.polymerase_dilution_mix_ratio()
@options.sequencing_polymerase_ratio()
@click.pass_context
def revio_abc_volumes(
    ctx: click.Context,
    volume_udf: str,
    preset_volume: str,
    factor: str,
    annealing_reagent_ratio: str,
    polymerase_buffer_ratio: str,
    polymerase_dilution_mix_ratio: str,
    sequencing_polymerase_ratio: str,
):
    """Calculate and set the reagent volumes needed for the ABC procedure for SMRTbell libraries."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process)
        for artifact in artifacts:
            if not artifact.udf.get(volume_udf):
                error_message = "Missing a library volume for one or more samples!"
                LOG.error(error_message)
                raise MissingValueError(error_message)
            elif preset_volume:
                preset_volume: float = float(preset_volume)
            sample_volume: float = get_artifact_volume(artifact=artifact, volume_udf=volume_udf)
            annealing_mix_volume: float = sample_volume
            polymerase_dilution_volume: float = calculate_per_sample_mix_volumes(
                volume_udf=sample_volume,
                ratio=polymerase_dilution_mix_ratio,
            )
            beads_volume: float = calculate_beads_per_sample(
                volume_udf=sample_volume,
                annealing_volume=annealing_mix_volume,
                polymerase_dilution_volume=polymerase_dilution_volume,
            )
            set_reagent_volumes_per_sample(
                artifact=artifact,
                annealing_mix_volume=annealing_mix_volume,
                polymerase_dilution_volume=polymerase_dilution_volume,
                beads_volume=beads_volume,
                elution_volume=preset_volume,
            )
        total_sample_volume: float = calculate_total_sample_volume(
            artifacts=artifacts, volume_udf=volume_udf
        )
        set_total_ABC_volumes(
            process=process,
            factor=factor,
            total_sample_volume=total_sample_volume,
            annealing_reagent_ratio=annealing_reagent_ratio,
            polymerase_buffer_ratio=polymerase_buffer_ratio,
            polymerase_dilution_mix_ratio=polymerase_dilution_mix_ratio,
            sequencing_polymerase_ratio=sequencing_polymerase_ratio,
        )
        message: str = "ABC volumes have been calculated for all artifacts and process UDFs!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
