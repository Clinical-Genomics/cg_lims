import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import FailingQCError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_qc_output_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact

LOG = logging.getLogger(__name__)


def get_qc(source: str, conc: float, amount: float) -> str:
    """QC-criteria depends on sample source, total amount and sample concentration. See AMS doc 1117, 1993 and 2125.
    The volume is subtracted by 3 in the calculations. This is beacause the lab uses 3 ul in the initial qc measurements.
    """

    qc = "FAILED"

    if source == "cfDNA":
        if amount >= 10 and conc <= 250 and conc >= 0.2:
            qc = "PASSED"
    else:
        if amount >= 500 and conc <= 250 and conc >= 8.33:
            qc = "PASSED"

    return qc


def calculate_amount_and_set_qc(artifacts: List[Artifact]) -> None:
    """Calculate amount and set qc for twist samples"""

    missing_udfs_count = 0
    qc_fail_count = 0
    for artifact in artifacts:
        sample = get_one_sample_from_artifact(artifact)
        source = sample.udf.get("Source")
        vol = artifact.udf.get("Volume (ul)")
        conc = artifact.udf.get("Concentration")
        if None in [source, conc, vol]:
            missing_udfs_count += 1
            continue

        amount = conc * (vol - 3)
        artifact.udf["Amount (ng)"] = amount
        qc = get_qc(source, conc, amount)
        if qc == "FAILED":
            qc_fail_count += 1
            LOG.info(
                f"Sample {sample.id} failed qc. Source: {source} Amount: {amount} Concentration: {conc}"
            )
        artifact.qc_flag = qc
        artifact.put()

    if missing_udfs_count:
        raise MissingUDFsError(f"Udf missing for {missing_udfs_count} sample(s).")
    if qc_fail_count:
        raise FailingQCError(
            f"Amounts have been calculated and qc flags set for all samples. QC failed for {qc_fail_count} sample(s)."
        )


@click.command()
@click.pass_context
def twist_qc_amount(ctx):
    """Calculates amount of samples for qc validation."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_qc_output_artifacts(lims=lims, process=process)
        calculate_amount_and_set_qc(artifacts)
        message = "Amounts have been calculated and qc flags set for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
