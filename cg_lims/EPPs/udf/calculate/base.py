#!/usr/bin/env python

import click

from cg_lims.EPPs.udf.calculate.twist_aliquot_amount import twist_aliquot_amount
from cg_lims.EPPs.udf.calculate.twist_aliquot_volume import twist_aliquot_volume
from cg_lims.EPPs.udf.calculate.twist_get_volumes_from_buffer import get_volumes_from_buffer
from cg_lims.EPPs.udf.calculate.calculate_water import volume_water
from cg_lims.EPPs.udf.calculate.molar_concentration import molar_concentration
from cg_lims.EPPs.udf.calculate.sum_missing_reads_in_pool import missing_reads_in_pool

# commands
from cg_lims.EPPs.udf.calculate.twist_pool import twist_pool
from cg_lims.EPPs.udf.calculate.twist_qc_amount import twist_qc_amount
from cg_lims.EPPs.udf.calculate.get_missing_reads import get_missing_reads
from cg_lims.EPPs.udf.calculate.calculate_amount_ng import calculate_amount_ng


@click.group(invoke_without_command=True)
@click.pass_context
def calculate(ctx):
    """Main entry point of calculate commands"""
    pass


calculate.add_command(twist_pool)
calculate.add_command(twist_aliquot_amount)
calculate.add_command(twist_aliquot_volume)
calculate.add_command(twist_qc_amount)
calculate.add_command(get_volumes_from_buffer)
calculate.add_command(get_missing_reads)
calculate.add_command(calculate_amount_ng)
calculate.add_command(volume_water)
calculate.add_command(molar_concentration)
calculate.add_command(missing_reads_in_pool)
