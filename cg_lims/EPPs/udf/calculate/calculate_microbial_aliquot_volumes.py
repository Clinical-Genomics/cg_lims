"""
CLI module to calculate the resuspension buffer volume (RB Volume) based on the amount of DNA
needed, as specified in the step `CG002 - Normalization of microbial samples for sequencing`
"""
import logging
import sys
from typing import List, Optional

import click
from genologics.entities import Artifact
from pydantic import BaseModel, ValidationError, validator

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts

FINAL_CONCENTRATION = 2
LOG = logging.getLogger(__name__)
MAXIMUM_CONCENTRATION = 60
QC_FAILED = "FAILED"
QC_PASSED = "PASSED"


class MicrobialAliquotVolumes(BaseModel):
    """Pydantic model for calculating microbial aliquot volumes based on the sample concentration"""

    sample_concentration: Optional[float]
    artifact_name: str
    is_ntc_sample: Optional[bool]
    sample_volume: Optional[float]
    total_volume: Optional[float]
    buffer_volume: Optional[float]
    qc_flag: Optional[str]

    @validator("sample_concentration", always=True)
    def set_sample_concentration(cls, v, values):
        """Set sample concentration and handle missing concentration udf"""
        if v is None:
            message = "Concentration udf missing on sample"
            LOG.error(message)
            raise ValueError(message)
        return v

    @validator("is_ntc_sample", always=True)
    def set_is_ntc_sample(cls, v, values):
        """Sets if the sample is and NFT sample or not"""
        ntc_sample_name = values.get("artifact_name")
        return ntc_sample_name.startswith("NTC-CG")

    @validator("sample_volume", always=True)
    def set_sample_volume(cls, v, values):
        """Calculate and set sample volume"""
        sample_concentration = values.get("sample_concentration")
        is_ntc_sample = values.get("is_ntc_sample")
        if is_ntc_sample:
            return 0
        if sample_concentration < FINAL_CONCENTRATION:
            return 15
        elif FINAL_CONCENTRATION <= sample_concentration <= 7.5:
            total_volume = 15
            sample_volume = (
                float(FINAL_CONCENTRATION * total_volume) / sample_concentration
            )
            buffer_volume = total_volume - sample_volume
            if buffer_volume < 2:
                return 15
            else:
                return sample_volume
        elif 7.5 <= sample_concentration <= MAXIMUM_CONCENTRATION:
            return 4

    @validator("total_volume", always=True)
    def set_total_volume(cls, v, values):
        """Calculate and set total volume"""
        sample_concentration = values.get("sample_concentration")
        is_ntc_sample = values.get("is_ntc_sample")
        if is_ntc_sample:
            return 15
        if sample_concentration <= 7.5:
            return 15
        elif 7.5 < sample_concentration <= MAXIMUM_CONCENTRATION:
            return (
                sample_concentration * values.get("sample_volume")
            ) / FINAL_CONCENTRATION

    @validator("buffer_volume", always=True)
    def set_buffer_volume(cls, v, values):
        """Calculate and set buffer volume"""
        sample_concentration = values.get("sample_concentration")
        is_ntc_sample = values.get("is_ntc_sample")
        if is_ntc_sample:
            return 15
        if sample_concentration < FINAL_CONCENTRATION:
            return 0
        elif FINAL_CONCENTRATION <= sample_concentration <= 60:
            return values.get("total_volume") - values.get("sample_volume")

    @validator("qc_flag", always=True)
    def set_qc_flag(cls, v, values):
        """Set the QC flag on a sample"""
        is_ntc_sample = values.get("is_ntc_sample")
        if values.get("sample_concentration") <= MAXIMUM_CONCENTRATION or is_ntc_sample:
            return QC_PASSED
        else:
            return QC_FAILED


def calculate_volume(artifacts: List[Artifact]) -> None:
    """Determines the total volume, water volume, and sample volume"""
    failed_artifacts = []

    for artifact in artifacts:
        try:
            volumes = MicrobialAliquotVolumes(
                sample_concentration=artifact.udf.get("Concentration"),
                artifact_name=artifact.samples[0].name,
            )
            artifact.qc_flag = volumes.qc_flag
            if volumes.qc_flag == QC_PASSED:
                artifact.udf["Total Volume (uL)"] = volumes.total_volume
                artifact.udf["Volume Buffer (ul)"] = volumes.buffer_volume
                artifact.udf["Sample Volume (ul)"] = volumes.sample_volume
                click.echo(volumes)
            artifact.put()
        except (Exception, ValidationError):
            LOG.warning(
                f"Could not calculate aliquot volumes for sample {artifact.id}."
            )
            failed_artifacts.append(artifact)
            continue

    if failed_artifacts:
        raise LimsError(
            f"Microbial aliquot volume calculations failed for {len(failed_artifacts)} samples, "
            f"{len(artifacts) - len(failed_artifacts)} updates successful. "
        )


@click.command()
@click.pass_context
def calculate_microbial_aliquot_volumes(context: click.Context):
    """Calculate microbial aliquot volumes based on the Concentration udf"""
    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_volume(artifacts=artifacts)
        message = "Microbial aliquot volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
