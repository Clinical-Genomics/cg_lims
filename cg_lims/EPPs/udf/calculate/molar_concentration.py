import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims import options

LOG = logging.getLogger(__name__)


def calculate_concentrations(
    artifacts: List[Artifact], size_udf: str, molar_concentration_udf: str, concentration_udf: str
) -> None:
    """
    Formula to calculate molar concentration (nM) from weight concentration (ng/ul) and fragment size (bp) is:

    molar_concentration = concentration * 1e6 / (average_molecular_weight * strands * fragment_size)

    where:
    - fragment_size is the number of base pairs of the DNA fragment (bp)
    - concentration is the concentration of dna (ng/ul)
    - average_molecular_weight = 328.3 is the average molecular weight of nucleotides, in g/mol.
    - strands = (one/two) for single or double stranded DNA
    - molar_concentration (nM)
    """
    average_molecular_weight = 328.3
    strands = 2
    missing_udfs_count = 0

    for artifact in artifacts:
        size = artifact.udf.get(size_udf)
        concentration = artifact.udf.get(concentration_udf)
        if None in [size, concentration]:
            missing_udfs_count += 1
            continue
        factor = 1e6 / (average_molecular_weight * strands * float(size))
        artifact.udf[molar_concentration_udf] = concentration * factor
        artifact.put()
    if missing_udfs_count:
        passed_artifacts = len(artifacts) - missing_udfs_count
        raise MissingUDFsError(
            f"Udf missing for {missing_udfs_count} sample(s). Concentration calculated for {passed_artifacts} samples."
        )


@click.command()
@options.input()
@options.size_udf()
@options.concantration_nm_udf()
@options.concantration_udf()
@click.pass_context
def molar_concentration(ctx, input: bool, size_udf: str, conc_nm_udf: str, conc_udf: str) -> None:
    """Script to calculate molar concentration given the weight concentration and fragment size. """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=input)
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
