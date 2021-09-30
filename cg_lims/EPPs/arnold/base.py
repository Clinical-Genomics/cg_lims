#!/usr/bin/env python

import click

from cg_lims.EPPs.arnold.prep_microbial import microbial_prep_document
from cg_lims.EPPs.arnold.prep_sars_cov_2 import sars_cov_2_prep_document
from cg_lims.EPPs.arnold.sample import sample


@click.group(invoke_without_command=True)
@click.pass_context
def arnold_upload(ctx):
    """Main load commands."""
    pass


arnold_upload.add_command(microbial_prep_document)
arnold_upload.add_command(sars_cov_2_prep_document)
arnold_upload.add_command(sample)
