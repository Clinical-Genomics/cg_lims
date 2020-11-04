from genologics.entities import Artifact

import logging
import sys
import click
from typing import List

from cg_lims.exceptions import LimsError, MissingUDFsError, FailingQCError
from cg_lims.get.artifacts import get_qc_messuements
from cg_lims.get.samples import get_artifact_sample

LOG = logging.getLogger(__name__)


def get_qc(source: str, conc: float, amount: float) -> str:
    """"""

    qc = "FAILED"

    if source == "cfDNA":
        if amount >= 10 and conc <= 250 and amount / 1.0 >= conc >= amount / 50.0:
            qc = "PASSED"
    else:
        if amount >= 300 and conc <= 250 and amount / 1.0 >= conc >= amount / 30.0:
            qc = "PASSED"

    return qc


def calculate_amount_and_set_qc(artifacts: List[Artifact]) -> None:
    """Calculate amount and set qc for twist samples"""

    missing_udfs_count = 0
    qc_fail_count = 0
    for artifact in artifacts:
        sample = get_artifact_sample(artifact)
        source = sample.udf.get("Source")
        vol = artifact.udf.get("Volume (ul)")
        conc = artifact.udf.get("Concentration")
        if None in [source, conc, vol]:
            missing_udfs_count += 1
            continue

        amount = conc * vol
        artifact.udf["Amount (ng)"] = amount
        qc = get_qc(source, conc, amount)
        if qc == "FAILED":
            qc_fail_count +=1
        artifact.qc_flag = get_qc(source, conc, amount)
        artifact.put()

    if missing_udfs_count:
        raise MissingUDFsError(f"Udf missing for {missing_udfs_count} samples")
    if qc_fail_count:
        raise FailingQCError(f"QC failed for {qc_fail_count} samples")


@click.command()
@click.pass_context
def twist_qc_amount(ctx):
    """Calculates amount of samples for qc validation."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_qc_messuements(lims=lims, process=process)
        calculate_amount_and_set_qc(artifacts)
        message = "Amounts have been calculated and qc flags set for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
