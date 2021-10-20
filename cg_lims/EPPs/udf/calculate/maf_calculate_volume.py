"""
CLI module to calculate dilution volumes from Concentration udf

For an explanation of the sample volume calculation and setting of the QG flag, see
AM-document 1243 Method - Preparing Plate for Genotyping, section 3.3.2 Preparing the plate
"""

import logging
import sys
from typing import List, Tuple, Optional

import click
from genologics.entities import Artifact
from pydantic import BaseModel, validator

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

FINAL_CONCENTRATION = 4
CONCENTRATION_UPPER_LIMIT = 1444
LOW_CONCENTRATION_THRESHOLD = 20
MINIMUM_TOTAL_VOLUME = 15
MAXIMUM_WATER_VOLUME = 180
QC_FAILED = "FAILED"
QC_PASSED = "PASSED"
STANDARD_SAMPLE_VOLUME = 3


class MafVolumes(BaseModel):
    sample_concentration: float
    sample_volume: Optional[float]
    final_volume: Optional[float]
    water_volume: Optional[float]
    qc_flag: Optional[str]

    @validator("sample_concentration", always=True)
    def set_sample_concentration(cls, v, values):
        if v < FINAL_CONCENTRATION:
            logging.exception("Too low or Missing concentration")
            raise ValueError()
        return v

    @validator("sample_volume", always=True)
    def set_sample_volume(cls, v, values):
        sample_conc = values["sample_concentration"]
        if sample_conc < 20:
            return MINIMUM_TOTAL_VOLUME * FINAL_CONCENTRATION / sample_conc
        elif 20 <= sample_conc < 244:
            return 3
        elif 244 <= sample_conc < 364:
            return 2
        elif 364 <= sample_conc < 724:
            return 1
        elif 724 <= sample_conc < 1444:
            return 0.5
        else:
            logging.exception("sample concentration not in valid range")
            raise ValueError()

    @validator("water_volume", always=True)
    def set_water_volume(cls, v, values):
        return values["final_volume"] - values["sample_volume"]

    @validator("final_volume", always=True)
    def set_final_volume(cls, v, values):
        """Calculates the final volume for a sample"""
        return values["sample_volume"] * values["sample_concentration"] / FINAL_CONCENTRATION

    @validator("qc_flag", always=True)
    def set_qc_flag(cls, v, values):
        if values["sample_volume"] == 3:
            return QC_PASSED
        else:
            return QC_FAILED


def calculate_volume(artifacts: List[Artifact]) -> None:
    """Determines the final volume, water volume, and sample volume"""
    failed_artifacts = []

    for artifact in artifacts:
        try:
            volumes = MafVolumes(sample_concentration=artifact.udf.get("Concentration"))
            artifact.qc_flag = volumes.qc_flag
            artifact.udf["Final Volume (uL)"] = volumes.final_volume
            artifact.udf["Volume H2O (ul)"] = volumes.water_volume
            artifact.udf["Volume of sample (ul)"] = volumes.sample_volume
            artifact.put()
        except Exception:
            LOG.warning(f"Could not calculate sample volume for sample {artifact.samples[0].name}.")
            failed_artifacts.append(artifact)
            continue
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
