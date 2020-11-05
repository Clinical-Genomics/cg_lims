#!/usr/bin/env python

import click

# commands
from cg_lims.EPPs.udf.calculate.twist_pool import twist_pool
from cg_lims.EPPs.udf.calculate.twist_aliquot_amount import twist_aliquot_amount
from cg_lims.EPPs.udf.calculate.twist_aliquot_volume import twist_aliquot_volume
from cg_lims.EPPs.udf.calculate.twist_get_volumes_from_buffer import get_volumes_from_buffer


@click.group(invoke_without_command=True)
@click.pass_context
def calculate(ctx):
    """Main entry point of calculate commands"""
    pass


calculate.add_command(twist_pool)
calculate.add_command(twist_aliquot_amount)
calculate.add_command(twist_aliquot_volume)
calculate.add_command(get_volumes_from_buffer)
