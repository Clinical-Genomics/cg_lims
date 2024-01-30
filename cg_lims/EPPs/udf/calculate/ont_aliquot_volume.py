import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.EPPs.udf.calculate.constants import (
    AVERAGE_MOLECULAR_WEIGHT_DS_DNA,
    AVERAGE_MOLECULAR_WEIGHT_DS_DNA_ENDS,
)
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte, get_sample_artifact
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims.get.udfs import get_udf
from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_original_fragment_size(sample_id: str, lims: Lims, size_udf: str) -> int:
    """Return the sample fragment size measured during reception control QC."""
    sample = Sample(lims=lims, id=sample_id)
    sample_artifact = get_sample_artifact(lims=lims, sample=sample)
    return sample_artifact.udf.get(size_udf)


def get_latest_fragment_size(
    sample_id: str, lims: Lims, size_udf: str, process_types: Optional[List[str]]
) -> int:
    """Return the most recently measured fragment size of a sample."""
    original_size = get_original_fragment_size(sample_id=sample_id, lims=lims, size_udf=size_udf)
    if not process_types:
        return original_size

    size_history = [original_size]

    for process_type in process_types:
        try:
            artifact = get_latest_analyte(
                lims=lims, sample_id=sample_id, process_types=[process_type]
            )
            if artifact.udf.get(size_udf):
                size_history.append(artifact.udf.get(size_udf))
        except MissingArtifactError:
            LOG.info(
                f"No artifact found for sample {sample_id} from process type {process_type}. Skipping."
            )
            continue
    LOG.info(f"Found fragment size history of sample {sample_id}: {size_history}")

    return size_history[-1]


def get_max_volume(process: Process) -> float:
    """"""
    max_volume = process.udf.get("Total Volume (ul)")
    if not max_volume:
        raise MissingUDFsError("Process udf missing: Total Volume (ul)")
    return max_volume


def fmol_to_ng(amount_fmol: float, size_bp: int) -> float:
    """"""
    return (
        amount_fmol
        * (size_bp * AVERAGE_MOLECULAR_WEIGHT_DS_DNA + AVERAGE_MOLECULAR_WEIGHT_DS_DNA_ENDS)
        / 10**6
    )


def get_sample_volume_ng(max_volume: float, amount_ng: float, concentration: float) -> float:
    """"""
    return min(max_volume, amount_ng / float(concentration))


def set_volumes(artifact: Artifact, sample_volume: float, max_volume: float) -> None:
    """"""
    artifact.udf["Sample Volume (ul)"] = sample_volume
    artifact.udf["Volume H2O (ul)"] = max_volume - sample_volume
    artifact.put()


@click.command()
@options.process_types()
@options.concentration_udf_option()
@options.size_udf()
@options.measurement()
@options.input()
@click.pass_context
def ont_aliquot_volume(
    ctx: click.Context,
    process_types: List[str],
    concentration_udf: str,
    size_udf: str,
    measurement: bool = False,
    input: bool = False,
):
    """"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_artifacts(process=process, measurement=measurement, input=input)
        failed_samples = []

        for artifact in artifacts:
            amount_needed_fmol = artifact.udf.get("Amount needed (fmol)")
            amount_needed_ng = artifact.udf.get("Amount needed (ng)")
            if not amount_needed_ng and not amount_needed_fmol:
                raise MissingUDFsError(
                    "You need to assign an amount needed (in either ng or fmol) for all samples!"
                )
            concentration = float(get_udf(entity=artifact, udf=concentration_udf))
            sample = get_one_sample_from_artifact(artifact=artifact)
            if amount_needed_fmol:
                size_bp = get_latest_fragment_size(
                    sample_id=sample.id, lims=lims, size_udf=size_udf, process_types=process_types
                )
                amount_needed_ng = fmol_to_ng(amount_fmol=amount_needed_fmol, size_bp=size_bp)

            max_volume = get_max_volume(process=process)
            sample_volume = get_sample_volume_ng(
                max_volume=max_volume, amount_ng=amount_needed_ng, concentration=concentration
            )
            if sample_volume == max_volume:
                message = (
                    f"Warning: The concentration ({concentration} ng/ul) of sample {sample.id} is too low in order to "
                    f"reach required amount of {amount_needed_ng} ng in {max_volume} ul. Set Sample Volume (ul) to {max_volume} ul."
                )
                LOG.info(message)
                failed_samples.append(sample.id)
            set_volumes(artifact=artifact, sample_volume=sample_volume, max_volume=max_volume)

        if failed_samples:
            raise MissingUDFsError(
                f"Warning: {len(failed_samples)} sample(s) didn't have a high enough concentration for the amount needed."
                f" See the log for further details."
            )
        message = "Aliquot volumes have been calculated for all artifacts."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
