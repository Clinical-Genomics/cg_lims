"""CLI module to set Reads Missing (M) udf on new samples"""
import logging
import sys
from typing import List

import click
from genologics.entities import Sample

from cg_lims.exceptions import LimsError, MissingCgFieldError, MissingUDFsError
from cg_lims.get.samples import get_process_samples
from cg_lims.status_db_api import StatusDBAPI

LOG = logging.getLogger(__name__)
PASSED = "PASSED"
FAILED = "FAILED"


def set_reads_missing_on_sample(sample: Sample, status_db: StatusDBAPI):
    """ """
    app_tag = get_app_tag(sample)
    target_amount = get_target_amount(app_tag, status_db)
    sample.udf["Reads missing (M)"] = target_amount / 1000000
    sample.put()


def get_app_tag(sample: Sample):
    """ """
    try:
        return sample.udf["Sequencing Analysis"]
    except Exception:
        raise MissingUDFsError(
            f"UDF Sequencing Analysis not found on sample {sample.id}!"
        )


def get_target_amount(app_tag: str, status_db: StatusDBAPI):
    """ """
    try:
        return status_db.apptag(tag_name=app_tag, key="target_reads")
    except ConnectionError:
        raise LimsError(message="No connection to clinical-api!")


def set_reads_missing(samples: List[Sample], status_db: StatusDBAPI):
    """ """
    failed_samples = 0
    for sample in samples:
        try:
            set_reads_missing_on_sample(sample, status_db)
        except Exception:
            failed_samples += 1
    return failed_samples


@click.command()
@click.pass_context
def set_reads_missing_on_new_samples(context: click.Context):
    """Set Reads Missing (M) udf on samples before they go into any workflow"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")

    process = context.obj["process"]
    status_db = context.obj["status_db"]

    try:
        samples = get_process_samples(process=process)
        failed_samples = set_reads_missing(samples, status_db)
        message = "Reads Missing (M) udf set on samples."
        if failed_samples:
            LOG.error(message)
            click.echo(message)
        else:
            LOG.info(message)
            click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
        pass
