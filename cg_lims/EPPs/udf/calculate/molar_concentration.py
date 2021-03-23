import logging
import sys
from typing import List, Optional

import click
from genologics.entities import Artifact

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims import options
from pydantic import BaseModel, Field

LOG = logging.getLogger(__name__)


def calculate_concentrations(
    artifacts: List[Artifact], size_udf: str, molar_concentration_udf: str, concentration_udf: str
) -> None:
    """
    Formula to calculate molar concentration (nM) from weight concentration (ng/ul) and fragment size (bp) is:

    molar_concentration = concentration * 1e6 / (average_molecular_weight * strands * fragment_size)

    where:
    fragment_size is the number of base pares of the DNA fragment (bp)
    concentration is the concentration of dna (ng/ul)
    average_molecular_weight = 328.3 is the average molecular weight of nucleotides, in g/mol.
    strands = (one/two) for single or double stranded DNA
    molar_concentration (nM)
    """
    average_molecular_weight = 328.3
    strands = 2

    passed_arts = 0
    missing_udfs_count = 0
    for art in artifacts:
        size = art.udf.get(size_udf)
        concentration = art.udf.get(concentration_udf)
        if None in [size, concentration]:
            missing_udfs_count += 1
            continue
        factor = 1e6 / (average_molecular_weight * strands * float(size))
        art.udf[molar_concentration_udf] = concentration * factor
        art.put()
        passed_arts += 1
    if missing_udfs_count:
        raise MissingUDFsError(
            f"Udf missing for {missing_udfs_count} sample(s). Concentration calculated for {passed_arts} samples."
        )


class ArtifactUDFs(BaseModel):
    size_base_pairs: Optional[int] = Field(None, alias="Size (bp)")
    average_size_base_pairs: Optional[float] = Field(None, alias="Average Size (bp)")
    concentration: float = Field(..., alias="Concentration")


AVERAGE_MOLECULAR_WEIGHT = 328.3
STRANDS = 2
FORMULA = 1e6 / (AVERAGE_MOLECULAR_WEIGHT * STRANDS)


def calculate_concentration(udf: ArtifactUDFs) -> float:

    return udf.concentration / udf.size_base_pairs * FORMULA


def add_concentration(artifact: Artifact, conc_nm_udf: str) -> None:
    udf_object = ArtifactUDFs(**artifact.udf)
    artifact.udf[conc_nm_udf] = calculate_concentrations(udf_object)
    artifact.put()


def update_artifacts(artifacts: List[Artifact], conc_nm_udf: str) -> None:
    for artifact in artifacts:
        add_concentration(artifact=artifact, conc_nm_udf=conc_nm_udf)


@click.command()
@options.input()
@click.option("--size-average", is_flag=True)
@options.concantration_nm_udf()
@click.pass_context
def molar_concentration(ctx, input: bool, size_average: bool, conc_nm_udf: str) -> None:
    """Script to calculate molar concentration given the weight concentration and fragment size. """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=input)

        calculate_concentrations(
            artifacts=artifacts,
            size_udf=size_udf,
            molar_concentration_udf=conc_nm_udf,
            concentration_udf=conc_udf,
        )
        message = "Concentration (nM) have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
