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
    beads_volume: float = artifact.udf[volume_udf]
    artifact.udf["Volume Cleanup Beads (ul)"] = round(beads_volume, 2)
    artifact.put()


def set_annealing_mix_per_sample(artifact: Artifact, volume_udf: str) -> None:
    """Set the volume Annealing mix to add per sample."""
    annealing_mix_volume: float = artifact.udf[volume_udf]
    artifact.udf["Volume Annealing Mix (ul)"] = round(annealing_mix_volume, 2)
    artifact.put()


def set_polymerase_dilution_mix_per_sample(
    artifact: Artifact, volume_udf: str, polymerase_dilution_mix_ratio: str
) -> None:
    """Set the volume Polymerase Dilution Mix to add per sample."""
    polymerase_dilution_volume: float = (
        float(polymerase_dilution_mix_ratio) * artifact.udf[volume_udf]
    )
    artifact.udf["Volume Polymerase Dilution Mix (ul)"] = round(
        polymerase_dilution_volume, 2
    )
    artifact.put()


def calculate_and_set_total_ABC_volumes(
    process: Process,
    artifacts: List[Artifact],
    factor: str,
    volume_udf: str,
    annealing_reagent_ratio: str,
    polymerase_buffer_ratio: str,
    polymerase_dilution_mix_ratio: str,
    sequencing_polymerase_ratio: str,
) -> None:
    """Calculate and set the total master mix and reagent volumes needed for all samples in the step. 
    Adding some excess specified in the cli command."""
    total_sample_volume: float = calculate_total_sample_volume(
        artifacts=artifacts, volume_udf=volume_udf
    )

    process.udf["Total Annealing Mix Volume (ul)"] = round(
        float(factor) * total_sample_volume, 1
    )
    process.udf["Annealing Buffer Volume (ul)"] = round(
        float(factor) * float(annealing_reagent_ratio) * total_sample_volume, 1
    )
    process.udf["Standard Sequencing Primer Volume (ul)"] = round(
        float(factor) * float(annealing_reagent_ratio) * total_sample_volume, 1
    )
    process.udf["Total Polymerase Dilution Mix Volume (ul)"] = round(
        float(factor) * float(polymerase_dilution_mix_ratio) * total_sample_volume, 1
    )
    process.udf["Polymerase Buffer Volume (ul)"] = round(
        float(factor) * float(polymerase_buffer_ratio) * total_sample_volume, 1
    )
    process.udf["Sequencing Polymerase Volume (ul)"] = round(
        float(factor) * float(sequencing_polymerase_ratio) * total_sample_volume, 1
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

        for artifact in artifacts:
            if artifact.udf.get(volume_udf) == None:
                error_message = (
                "Missing a value for one or more sample volumes.")
                LOG.error(error_message)
                raise MissingValueError(error_message)
            set_annealing_mix_per_sample(artifact=artifact, volume_udf=volume_udf)
            set_polymerase_dilution_mix_per_sample(
                artifact=artifact,
                volume_udf=volume_udf,
                polymerase_dilution_mix_ratio=polymerase_dilution_mix_ratio,
            )
            set_beads_per_sample(artifact=artifact, volume_udf=volume_udf)
        calculate_and_set_total_ABC_volumes(
            process=process,
            artifacts=artifacts,
            factor=factor,
            volume_udf=volume_udf,
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
