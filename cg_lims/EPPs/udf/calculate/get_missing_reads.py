import logging
import sys

import click
from genologics.entities import Artifact
from requests.exceptions import ConnectionError

from cg_lims.exceptions import LimsError, MissingCgFieldError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def set_artifact_rerun(
    target_amount_reads: float, guaranteed_fraction: float, reads_total: int, artifact: Artifact
):
    """Set Missing Reads, qc flag and Rerun"""
    target_amount = target_amount_reads / 1000000
    reads_min = target_amount * guaranteed_fraction
    reads_missing = reads_min - reads_total

    if reads_missing > 0:
        reads_to_sequence = target_amount - reads_total
        artifact.udf["Rerun"] = True
        artifact.qc_flag = "FAILED"
    else:
        reads_to_sequence = 0
        artifact.udf["Rerun"] = False
        artifact.qc_flag = "PASSED"

    for sample in artifact.samples:
        sample.udf["Reads missing (M)"] = reads_to_sequence
        sample.put()

    artifact.put()


def check_control(artifact: Artifact) -> bool:
    """Return True if all atrtifact samples are negative control samples."""
    return all(sample.udf.get("Control") == "negative" for sample in artifact.samples)


def find_reruns(artifacts: list, status_db) -> None:
    """
    Looking for artifacts to rerun.
    Negative control samples are never sent for rerun.
    A pool with any sample that is not a negative control will be sent for rerun if reads are missing."""
    failed_arts = 0
    for artifact in artifacts:
        if check_control(artifact):
            artifact.qc_flag = "PASSED"
            artifact.put()
            continue
        sample = artifact.samples[0]
        reads_total = sample.udf.get("Total Reads (M)")
        app_tag = sample.udf.get("Sequencing Analysis")

        if None in (app_tag, reads_total):
            failed_arts += 1
            continue

        try:
            target_amount_reads = status_db.apptag(tag_name=app_tag, key="target_reads")
            guaranteed_fraction = 0.01 * status_db.apptag(
                tag_name=app_tag, key="percent_reads_guaranteed"
            )
        except ConnectionError:
            raise LimsError(message="Could not communicate with cg server")
        except:
            raise MissingCgFieldError(f"Could not find application tag: {app_tag} in database.")

        set_artifact_rerun(target_amount_reads, guaranteed_fraction, reads_total, artifact)

    if failed_arts:
        raise MissingUDFsError(
            message=f"Could not update {failed_arts} artifacts due to missing UDFs"
        )


@click.command()
@click.pass_context
def get_missing_reads(ctx):
    """Script to calculate missing reads and decide on reruns.
    Negative control samples are never sent for rerun.
    A pool with any sample that is not a negative control will be sent for rerun if reads are missing."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    status_db = ctx.obj["status_db"]

    try:
        artifacts = get_artifacts(process=process, input=False)
        find_reruns(artifacts=artifacts, status_db=status_db)
        message = "Missing Reads and Rerun info have been set on all artifacts"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
