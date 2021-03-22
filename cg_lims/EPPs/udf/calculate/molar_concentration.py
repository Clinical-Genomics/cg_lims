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
    artifacts: List[Artifact], size_udf: str, conc_nm_udf: str, conc_udf: str
) -> None:
    passed_arts = 0
    missing_udfs_count = 0
    for art in artifacts:
        size = art.udf.get(size_udf)
        concentration = art.udf.get(conc_udf)
        if None in [size, concentration]:
            missing_udfs_count += 1
            continue
        factor = 1e6 / (328.3 * 2 * float(size))
        art.udf[conc_nm_udf] = concentration * factor
        art.put()
        passed_arts += 1
    if missing_udfs_count:
        raise MissingUDFsError(
            f"Udf missing for {missing_udfs_count} sample(s). Concentration calculated for {passed_arts} samples."
        )


@click.command()
@options.input()
@options.size_udf()
@options.concantration_nm_udf()
@options.concantration_udf()
@click.pass_context
def molar_concentration(ctx, input: bool, size_udf: str, conc_nm_udf: str, conc_udf: str) -> None:
    """Script to calculate molar concentration given the
    weight concentration, in Clarity LIMS. Before updating the artifacts,
    the script verifies that 'Concentration' and 'Size (bp)' udf:s are not blank,
    Artifacts that do not fulfill the requirements, will not be updated."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=input)
        calculate_concentrations(
            artifacts=artifacts, size_udf=size_udf, conc_nm_udf=conc_nm_udf, conc_udf=conc_udf
        )
        message = "Concentration (nM) have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
