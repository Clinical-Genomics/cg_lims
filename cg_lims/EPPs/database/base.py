#!/usr/bin/env python

import click

from cg_lims.EPPs.database.prep_microbial import microbial_prep_document


@click.group(invoke_without_command=True)
@click.pass_context
def database_upload(ctx):
    """Main load commands."""
    pass


database_upload.add_command(microbial_prep_document)
