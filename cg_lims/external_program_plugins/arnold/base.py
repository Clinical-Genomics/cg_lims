#!/usr/bin/env python

import click

from cg_lims.external_program_plugins.arnold.prep import prep
from cg_lims.external_program_plugins.arnold.sample import sample
from cg_lims.external_program_plugins.arnold.sequencing import sequencing
from cg_lims.external_program_plugins.arnold.flow_cell import flow_cell


@click.group(invoke_without_command=True)
@click.pass_context
def arnold_upload(ctx):
    """Main load commands."""
    pass


arnold_upload.add_command(flow_cell)
arnold_upload.add_command(prep)
arnold_upload.add_command(sample)
arnold_upload.add_command(sequencing)
