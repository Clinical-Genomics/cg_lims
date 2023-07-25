#!/usr/bin/env python
import click
from cg_lims.external_program_plugins.udf.calculate import calculate

# commands
from cg_lims.external_program_plugins.udf.copy import copy
from cg_lims.external_program_plugins.udf.set import set
from cg_lims.external_program_plugins.udf.check import check


@click.group(invoke_without_command=True)
@click.pass_context
def udf(ctx):
    """Main entry point of udf commands"""
    pass


udf.add_command(copy)
udf.add_command(calculate)
udf.add_command(set)
udf.add_command(check)
