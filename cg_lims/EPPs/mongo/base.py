#!/usr/bin/env python

import click

from cg_lims.EPPs.mongo.prep_microbial import microbial_prep_document


@click.group(invoke_without_command=True)
@click.pass_context
def mongo(ctx):
    """Main load commands."""
    pass


mongo.add_command(microbial_prep_document)
