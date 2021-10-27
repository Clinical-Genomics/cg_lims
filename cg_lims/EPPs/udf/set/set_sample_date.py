#!/usr/bin/env python
import logging

import click
from cg_lims.get.samples import get_process_samples
from datetime import datetime

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
def set_received(context: click.Context):
    """Script to set todays date on sample udf Received at"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    samples = get_process_samples(process=process)

    recieved_udf = "Received at"
    for sample in samples:
        if sample.udf.get(recieved_udf):
            LOG.warning(f"The sample {sample.id} already had a received date. Not updating.")
            continue
        sample.udf[recieved_udf] = datetime.today()
        sample.put()


@click.command()
@click.pass_context
def set_prepared(context: click.Context):
    """Script to set todays date on sample udf Library Prep Finished"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    samples = get_process_samples(process=process)

    for sample in samples:
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
        sample.udf["Library Prep Finished"] = datetime.today()
        sample.put()


@click.command()
@click.pass_context
def set_sequenced(context: click.Context):
    """Script to set todays date on sample udf Sequencing Finished"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    samples = get_process_samples(process=process)

    for sample in samples:
        if sample.udf.get("Delivered at"):
            LOG.warning(
                f"The sample {sample.id} had a delivery finished date which is now deleted since the sample is being "
                f"re sequenced. "
            )
            sample.udf["Delivered at"] = None
        sample.udf["Sequencing Finished"] = datetime.today()
        sample.put()


@click.command()
@click.pass_context
def set_delivered(context: click.Context):
    """Script to set todays date on sample udf Delivered at"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")
    process = context.obj["process"]
    samples = get_process_samples(process=process)

    for sample in samples:
        sample.udf["Delivered at"] = datetime.today()
        sample.put()
