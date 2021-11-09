"""
CLI module to calculate the resuspension buffer volume (RB Volume) based on the amount of DNA
needed, as specified in the step `CG002 - Normalization of microbial samples for sequencing`
"""
import logging
import sys
from typing import List, Optional

import click
from genologics.entities import Artifact
from pydantic import BaseModel, validator

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts

FINAL_CONCENTRATION = 2
LOG = logging.getLogger(__name__)
MAXIMUM_CONCENTRATION = 60
QC_FAILED = "FAILED"
QC_PASSED = "PASSED"


class MicrobialAliquotVolumes(BaseModel):
    """Pydantic model for calculating microbial aliquot volumes based on the sample concentration"""

    sample_concentration: float
    total_volume: Optional[float]
    volume_buffer: Optional[float]
    sample_volume: Optional[float]
    qc_flag: Optional[str]

    @validator("sample_concentration", always=True)
    def set_sample_concentration(cls, v, values):
        """Set sample concentration and handle high or missing concentration"""
        if v > MAXIMUM_CONCENTRATION:
            message = "Concentration is too high"
            LOG.error(message)
            raise ValueError(message)
        if not v:
            message = "Concentration is missing"
            LOG.error(message)
            raise ValueError(message)
        return v

    @validator("total_volume", always=True)
    def set_total_volume(cls, v, values):
        """#TODO: Docstring"""
        sample_concentration = values.get("sample_concentration")
        pass

    @validator("water_volume", always=True)
    def set_water_volume(cls, v, values):
        """Calculate the water volume for a sample"""
        return values.get("final_volume") - values.get("sample_volume")

    @validator("final_volume", always=True)
    def set_final_volume(cls, v, values):
        """Calculates the final volume for a sample"""
        return (
            values.get("sample_volume")
            * values.get("sample_concentration")
            / FINAL_CONCENTRATION
        )

    @validator("qc_flag", always=True)
    def set_qc_flag(cls, v, values):
        """Set the QC flag on a sample"""
        if values.get("sample_concentration") < MAXIMUM_CONCENTRATION:
            return QC_PASSED
        else:
            return QC_FAILED


def calculate_volume(artifacts: List[Artifact]) -> None:
    """Determines the total volume, water volume, and sample volume"""
    failed_artifacts = []

    for artifact in artifacts:
        try:
            volumes = MicrobialAliquotVolumes(
                sample_concentration=artifact.udf.get("Concentration")
            )
            artifact.qc_flag = volumes.qc_flag
            artifact.udf["Total Volume (uL)"] = volumes.total_volume
            # artifact.udf["Total Volume (uL)"] = buffer_volume + sample_volume
            artifact.udf["Volume Buffer (ul)"] = volumes.buffer_volume
            artifact.udf["Sample Volume (ul)"] = volumes.sample_volume
            artifact.put()
        except Exception:
            LOG.warning(f"Could not calculate sample volume for sample {artifact.id}.")
            failed_artifacts.append(artifact)
            continue
            pass


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
