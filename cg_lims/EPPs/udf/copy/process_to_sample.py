#!/usr/bin/env python
import logging
import sys

import click
from genologics.entities import Process
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.samples import get_process_samples



@click.command()
@options.sample_udf(help="Sample udf to set.")
@options.process_udf(help="Process udf to get.")
@click.pass_context
def process_to_sample(ctx, sample_udf, process_udf):
    """Script to copy Process udf to sample udf"""

    process = ctx.obj["process"]
    failed_samples = []

    udf = process.udf.get(process_udf)
    if not udf:
        sys.exit(f"Process udf: {process_udf} not set!")

    samples = get_process_samples(process=process)
    for sample in samples:
        try:
            sample.udf[sample_udf] = udf
            sample.put()
        except:
            failed_samples.append(sample)

    if not failed_samples:
        click.echo(f"Udf {sample_udf} have been set on all samples.")
    else:
        sys.exit(f"Could not set udfs on {len(failed_samples)} samples.")

