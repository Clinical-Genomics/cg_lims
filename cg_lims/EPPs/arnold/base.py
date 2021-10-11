#!/usr/bin/env python

import click

from cg_lims.EPPs.arnold.prep import prep
from cg_lims.EPPs.arnold.sample import sample


@click.group(invoke_without_command=True)
@click.pass_context
def arnold_upload(ctx):
    """Main load commands."""
    pass


arnold_upload.add_command(prep)
arnold_upload.add_command(sample)
