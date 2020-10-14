#!/usr/bin/env python

import click

# commands
from cg_lims.EPPs.move import move
from cg_lims.EPPs.files import files
from cg_lims.EPPs.udf import udf


@click.group(invoke_without_command=True)
@click.pass_context
def epps(ctx):
    """Main entry point of epp commands"""
    pass


epps.add_command(move)
epps.add_command(files)
epps.add_command(udf)
