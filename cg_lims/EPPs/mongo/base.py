#!/usr/bin/env python

import click

from cg_lims.EPPs.mongo.prep_microbial import microbial_prep_document


@click.group(invoke_without_command=True)
@click.pass_context
def mongo(ctx):
    """Main entry point of calculate commands"""
    pass


mongo.add_command(microbial_prep_document)
