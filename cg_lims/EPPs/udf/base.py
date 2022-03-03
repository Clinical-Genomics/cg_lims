#!/usr/bin/env python
import click
from cg_lims.EPPs.udf.calculate import calculate

# commands
from cg_lims.EPPs.udf.copy import copy
from cg_lims.EPPs.udf.set import set
from cg_lims.EPPs.udf.check import check


@click.group(invoke_without_command=True)
@click.pass_context
def udf(ctx):
    """Main entry point of udf commands"""
    pass


udf.add_command(copy)
udf.add_command(calculate)
udf.add_command(set)
udf.add_command(check)
