#!/usr/bin/env python

import click

from cg_lims.EPPs.udf.calculate.calculate_amount_ng import calculate_amount_ng
from cg_lims.EPPs.udf.calculate.calculate_beads import calculate_beads
from cg_lims.EPPs.udf.calculate.calculate_microbial_aliquot_volumes import (
    calculate_microbial_aliquot_volumes,
)
from cg_lims.EPPs.udf.calculate.calculate_resuspension_buffer_volumes import (
    calculate_resuspension_buffer_volume,
)
from cg_lims.EPPs.udf.calculate.calculate_water import volume_water
from cg_lims.EPPs.udf.calculate.calculate_water_volume_rna import (
    calculate_water_volume_rna,
)
from cg_lims.EPPs.udf.calculate.get_missing_reads import get_missing_reads
from cg_lims.EPPs.udf.calculate.maf_calculate_volume import maf_calculate_volume
from cg_lims.EPPs.udf.calculate.molar_concentration import molar_concentration
from cg_lims.EPPs.udf.calculate.sum_missing_reads_in_pool import missing_reads_in_pool
from cg_lims.EPPs.udf.calculate.twist_aliquot_amount import twist_aliquot_amount
from cg_lims.EPPs.udf.calculate.twist_aliquot_volume import twist_aliquot_volume
from cg_lims.EPPs.udf.calculate.twist_get_volumes_from_buffer import (
    get_volumes_from_buffer,
)
from cg_lims.EPPs.udf.calculate.calculate_average_size_and_set_qc import calculate_average_size_and_set_qc

# commands
from cg_lims.EPPs.udf.calculate.twist_pool import twist_pool
from cg_lims.EPPs.udf.calculate.twist_qc_amount import twist_qc_amount


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
calculate.add_command(calculate_beads)
calculate.add_command(missing_reads_in_pool)
calculate.add_command(maf_calculate_volume)
calculate.add_command(calculate_resuspension_buffer_volume)
calculate.add_command(calculate_water_volume_rna)
calculate.add_command(calculate_microbial_aliquot_volumes)
calculate.add_command(calculate_average_size_and_set_qc)
