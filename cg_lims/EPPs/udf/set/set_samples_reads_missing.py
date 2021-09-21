"""CLI module to set Reads Missing (M) udf on new samples"""
import logging
import sys
from typing import List

import click
from genologics.entities import Sample

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.samples import get_process_samples
from cg_lims.get.udfs import get_udf
from cg_lims.status_db_api import StatusDBAPI

LOG = logging.getLogger(__name__)


def get_target_amount(app_tag: str, status_db: StatusDBAPI) -> int:
    """Gets the target amount of reads from clinical-api"""
    return status_db.apptag(tag_name=app_tag, key="target_reads")


def set_reads_missing_on_sample(sample: Sample, status_db: StatusDBAPI) -> None:
    """Sets the udf "Reads missing (M)" on a sample to the target amount of reads bases on the app tag"""
    app_tag = get_udf(sample, "Sequencing Analysis")
    target_amount = get_target_amount(app_tag, status_db)
    sample.udf["Reads missing (M)"] = target_amount / 1000000
    sample.put()


def set_reads_missing(samples: List[Sample], status_db: StatusDBAPI) -> None:
    """Attempts to set the udf "Reads missing (M)" on all samples"""
    failed_samples_count = 0
    succeeded_samples_count = 0
    for sample in samples:
        try:
            set_reads_missing_on_sample(sample, status_db)
            succeeded_samples_count += 1
        except MissingUDFsError:
            failed_samples_count += 1

    if failed_samples_count:
        raise LimsError(
            f"Reads Missing (M) set on {succeeded_samples_count} sample(s), {failed_samples_count} sample(s) failed"
        )


@click.command()
@click.pass_context
def set_reads_missing_on_new_samples(context: click.Context):
    """Set Reads Missing (M) udf on samples before they go into any workflow"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")

    process = context.obj["process"]
    status_db = context.obj["status_db"]

    samples = get_process_samples(process=process)

    try:
        set_reads_missing(samples, status_db)
        message = f"Reads Missing (M) udf set on all sample(s)."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
