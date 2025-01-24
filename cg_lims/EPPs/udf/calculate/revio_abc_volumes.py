import logging
import sys
from typing import List

import click
from genologics.entities import Artifact, Process

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingValueError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def calculate_total_sample_volume(artifacts: List[Artifact], volume_udf: str) -> float:
    """Return the total volume of all samples in the step."""
    return sum(artifact.udf[volume_udf] for artifact in artifacts)


def set_beads_per_sample(artifact: Artifact, volume_udf: str) -> None:
    """Set the SMRTbell cleanup bead volume (1X of sample volume)."""
    beads_volume: float = round(artifact.udf[volume_udf], 2)
    artifact.udf["Volume Cleanup Beads (ul)"] = beads_volume
    artifact.put()


def set_annealing_mix_per_sample(artifact: Artifact, volume_udf: str) -> None:
    """Set the volume Annealing mix to add per sample."""
    annealing_mix_volume: float = round(artifact.udf[volume_udf], 2)
    artifact.udf["Volume Annealing Mix (ul)"] = annealing_mix_volume
    artifact.put()


def calculate_and_set_polymerase_dilution_mix_per_sample(
    artifact: Artifact, volume_udf: str, polymerase_dilution_mix_ratio: str
) -> None:
    """Set the volume Polymerase Dilution Mix to add per sample."""
    polymerase_dilution_volume: float = round(
        (float(polymerase_dilution_mix_ratio) * artifact.udf[volume_udf]), 2
    )
    artifact.udf["Volume Polymerase Dilution Mix (ul)"] = polymerase_dilution_volume
    artifact.put()


def calculate_total_ABC_volumes(
    factor: str, total_sample_volume: str, reagent_ratio: str = None
) -> float:
    """Calculate the total master mix and reagent volumes needed for all samples in the step.
    Adding some excess represented by factor."""
    if not reagent_ratio:
        reagent_ratio = 1
    return round(float(factor) * total_sample_volume * float(reagent_ratio), 1)


def set_total_ABC_volumes(
    process: Process,
    factor: str,
    total_sample_volume: str,
    annealing_reagent_ratio: str,
    polymerase_buffer_ratio: str,
    polymerase_dilution_mix_ratio: str,
    sequencing_polymerase_ratio: str,
) -> None:
    """Set the total master mix and reagent volumes needed for all samples in the step."""

    process.udf["Total Annealing Mix Volume (ul)"] = calculate_total_ABC_volumes(
        factor=factor, 
        total_sample_volume=total_sample_volume
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
@options.factor()
@options.annealing_reagent_ratio()
@options.polymerase_buffer_ratio()
@options.polymerase_dilution_mix_ratio()
@options.sequencing_polymerase_ratio()
@click.pass_context
def revio_abc_volumes(
    ctx: click.Context,
    volume_udf: str,
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
        total_sample_volume: float = calculate_total_sample_volume(
            artifacts=artifacts, volume_udf=volume_udf
        )

        for artifact in artifacts:
            if not artifact.udf.get(volume_udf):
                error_message = "Missing a value for one or more sample volumes!"
                LOG.error(error_message)
                raise MissingValueError(error_message)
            set_beads_per_sample(artifact=artifact, volume_udf=volume_udf)
            set_annealing_mix_per_sample(artifact=artifact, volume_udf=volume_udf)
            calculate_and_set_polymerase_dilution_mix_per_sample(
                artifact=artifact,
                volume_udf=volume_udf,
                polymerase_dilution_mix_ratio=polymerase_dilution_mix_ratio,
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
        message: str = (
            "ABC volumes have been calculated for all artifacts and process UDFs!"
        )
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
