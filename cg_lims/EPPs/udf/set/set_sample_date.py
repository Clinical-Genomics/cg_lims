"""Scripts to set the sample date udfs.
"""
import logging
from typing import Literal, List

import click
from genologics.entities import Sample, Process

from cg_lims import options
from cg_lims.get.samples import get_process_samples
from datetime import datetime

LOG = logging.getLogger(__name__)


def set_prepared(sample: Sample):
    """Script to set todays date on sample udf Library Prep Finished.
    If the sample has a delivery finished date and a sequencing finished date when
    this script is run, they are deleted.
    This is because the sample is assumed to be re sequenced and delivered again."""

    if sample.udf.get("Delivered at"):
        sample.udf["Delivered at"] = None
        LOG.warning(
            f"The sample {sample.id} had a delivery finished date which is now deleted since the sample is being "
            f"re prepped. "
        )
    if sample.udf.get("Sequencing Finished"):
        LOG.warning(
            f"The sample {sample.id} had a sequencing finished date which is now deleted since the sample is "
            f"being re prepped. "
        )
        sample.udf["Sequencing Finished"] = None
    sample.udf["Library Prep Finished"] = datetime.today().date()
    sample.put()


def set_sequenced(sample: Sample):
    """Script to set todays date on sample udf Sequencing Finished.
    If the sample has a delivery finished date when this script is run, it will be deleted.
    This is because the sample is assumed to be delivered again."""

    if sample.udf.get("Delivered at"):
        LOG.warning(
            f"The sample {sample.id} had a delivery finished date which is now deleted since the sample is being "
            f"re sequenced. "
        )
        sample.udf["Delivered at"] = None
    sample.udf["Sequencing Finished"] = datetime.today().date()
    sample.put()


def set_delivered(sample: Sample):
    """Script to set todays date on sample udf Delivered at.
    Overwriting any old delivery date."""

    sample.udf["Delivered at"] = datetime.today().date()
    sample.put()


date_functions = {
    "Library Prep Finished": set_prepared,
    "Sequencing Finished": set_sequenced,
    "Delivered at": set_delivered,
}


@click.command()
@options.sample_udf(help="Sample date udf to set.")
@click.pass_context
def set_sample_date(
    context: click.Context,
    sample_udf: Literal[
        "Received at", "Library Prep Finished", "Sequencing Finished", "Delivered at"
    ],
):
    """Script to set todays date on sample udf."""

    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process: Process = context.obj["process"]
    samples: List[Sample] = get_process_samples(process=process)
    set_date_function = date_functions.get(sample_udf)
    for sample in samples:
        set_date_function(sample=sample)
