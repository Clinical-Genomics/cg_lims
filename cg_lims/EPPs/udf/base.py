#!/usr/bin/env python

import click

# commands
from cg_lims.EPPs.udf.copy import copy
from cg_lims.EPPs.udf.calculate import calculate


@click.group(invoke_without_command=True)
@click.pass_context
def udf(ctx):
    """Main entry point of udf commands"""
    pass


udf.add_command(copy)
udf.add_command(calculate)
