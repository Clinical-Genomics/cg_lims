#!/usr/bin/env python

import click

from cg_lims.EPPs.udf.calculate import calculate

# commands
from cg_lims.EPPs.udf.copy import copy


@click.group(invoke_without_command=True)
@click.pass_context
def udf(ctx):
    """Main entry point of udf commands"""
    pass


udf.add_command(copy)
udf.add_command(calculate)
