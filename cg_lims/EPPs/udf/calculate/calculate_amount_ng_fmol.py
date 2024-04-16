import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.EPPs.udf.calculate.constants import (
    AVERAGE_MOLECULAR_WEIGHT_DS_DNA,
    AVERAGE_MOLECULAR_WEIGHT_DS_DNA_ENDS,
)
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingValueError
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte, get_sample_artifact
from genologics.entities import Artifact, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_original_fragment_size(sample_id: str, lims: Lims, size_udf: str) -> int:
    """Return the sample fragment size measured during reception control QC."""
    sample = Sample(lims=lims, id=sample_id)
    sample_artifact = get_sample_artifact(lims=lims, sample=sample)
    return sample_artifact.udf.get(size_udf)


def get_latest_fragment_size(
    artifact: Artifact, lims: Lims, size_udf: str, process_types: Optional[List[str]]
) -> int:
    """Return the most recently measured fragment size of a sample."""
    if artifact.udf.get(size_udf):
        return artifact.udf.get(size_udf)

    sample_id = artifact.samples[0].id
    original_size = get_original_fragment_size(sample_id=sample_id, lims=lims, size_udf=size_udf)

    if not process_types:
        return original_size

    size_history = [original_size]

    for process_type in process_types:
        try:
            previous_artifact = get_latest_analyte(
                lims=lims, sample_id=sample_id, process_types=[process_type]
            )
            if previous_artifact.udf.get(size_udf):
                size_history.append(previous_artifact.udf.get(size_udf))
        except MissingArtifactError:
            LOG.info(
                f"No artifact found for sample {sample_id} from process type {process_type}. Skipping."
            )
            continue
    LOG.info(f"Found fragment size history of sample {sample_id}: {size_history}")

    return size_history[-1]


def calculate_amount_ng(concentration: float, volume: float) -> float:
    """Calculate and return the amount (ng) given a concentration (ng/ul) and volume (ul)."""
    return concentration * volume


def calculate_amount_fmol(concentration: float, volume: float, size_bp: int) -> float:
    """
    Calculate and return the amount (fmol) given a concentration (ng/ul),
    volume (ul) and DNA fragment size in base pairs.
    The formula used for the mass to mole conversion was based on the one used in https://nebiocalculator.neb.com/#!/dsdnaamt
    """
    amount_ng = calculate_amount_ng(concentration=concentration, volume=volume)
    return (
        10**6
        * amount_ng
        / (size_bp * AVERAGE_MOLECULAR_WEIGHT_DS_DNA + AVERAGE_MOLECULAR_WEIGHT_DS_DNA_ENDS)
    )


def set_amounts(
    artifacts: List[Artifact],
    lims: Lims,
    process_types: List[str],
    concentration_udf: str,
    volume_udf: Optional[str],
    preset_volume: Optional[float],
    size_udf: str,
) -> None:
    """Calculates and sets the sample amounts in ng and fmol."""
    for artifact in artifacts:
        size_bp = get_latest_fragment_size(
            artifact=artifact,
            lims=lims,
            size_udf=size_udf,
            process_types=process_types,
        )
        concentration = artifact.udf.get(concentration_udf)
        if preset_volume:
            volume = float(preset_volume)
        elif volume_udf:
            volume = artifact.udf.get(volume_udf)
        else:
            raise MissingValueError(
                "Either a set volume or a given volume UDF name is required to calculate sample amounts!"
            )

        amount_ng = calculate_amount_ng(concentration=concentration, volume=volume)
        amount_fmol = calculate_amount_fmol(
            concentration=concentration, volume=volume, size_bp=size_bp
        )
        artifact.udf["Amount (ng)"] = amount_ng
        artifact.udf["Amount (fmol)"] = amount_fmol
        artifact.put()


@click.command()
@options.process_types()
@options.concentration_udf()
@options.volume_udf_option()
@options.preset_volume()
@options.size_udf()
@options.measurement()
@options.input()
@click.pass_context
def calculate_amount_ng_fmol(
    ctx: click.Context,
    process_types: List[str],
    concentration_udf: str,
    volume_udf: Optional[str],
    preset_volume: Optional[float],
    size_udf: str,
    measurement: bool = False,
    input: bool = False,
):
    """Calculates the sample amount of DNA in both fmol and ng.
    Requires concentration (ng/ul), volume (ul), and size (bp) to be known."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_artifacts(process=process, measurement=measurement, input=input)
        set_amounts(
            artifacts=artifacts,
            lims=lims,
            process_types=process_types,
            concentration_udf=concentration_udf,
            volume_udf=volume_udf,
            preset_volume=preset_volume,
            size_udf=size_udf,
        )

        message = "Amounts have been calculated for all artifacts."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
