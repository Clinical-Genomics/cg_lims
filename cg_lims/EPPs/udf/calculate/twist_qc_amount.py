import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import FailingQCError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims.get.udfs import get_maximum_amount
from genologics.entities import Artifact

LOG = logging.getLogger(__name__)

MAXIMUM_SAMPLE_AMOUNT = 250


def get_qc(source: str, conc: float, amount: float, max_amount: float) -> str:
    """QC-criteria depends on sample source, total amount and sample concentration. See AMS doc 1117, 1993 and 2125.
    The volume is subtracted by 3 in the calculations. This is because the lab uses 3 ul in the initial qc measurements.
    """

    qc = "FAILED"
    if source == "cell-free DNA" or source == "cfDNA":
        if amount >= 10 and 250 >= conc >= 0.2:
            qc = "PASSED"
    else:
        if amount >= max_amount and 250 >= conc >= 8.33:
            qc = "PASSED"
    return qc


def calculate_amount_and_set_qc(artifacts: List[Artifact], subtract_volume: str) -> None:
    """Calculate amount and set qc for twist samples"""

    missing_udfs_count = 0
    qc_fail_count = 0
    for artifact in artifacts:
        sample = get_one_sample_from_artifact(artifact=artifact)
        source = sample.udf.get("Source")
        vol = artifact.udf.get("Volume (ul)")
        conc = artifact.udf.get("Concentration")
        if None in [source, conc, vol]:
            missing_udfs_count += 1
            continue

        amount = conc * (vol - int(subtract_volume))
        artifact.udf["Amount (ng)"] = amount
        max_amount = get_maximum_amount(artifact=artifact, default_amount=MAXIMUM_SAMPLE_AMOUNT)
        qc = get_qc(source=source, conc=conc, amount=amount, max_amount=max_amount)
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
@options.subtract_volume()
@click.pass_context
def twist_qc_amount(
    ctx: click.Context,
    subtract_volume: str,
):
    """Calculates amount of samples for qc validation."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, measurement=True)
        calculate_amount_and_set_qc(artifacts=artifacts, subtract_volume=subtract_volume)
        message = "Amounts have been calculated and qc flags set for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
