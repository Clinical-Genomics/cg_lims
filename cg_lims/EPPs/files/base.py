#!/usr/bin/env python
import click

# commands
from cg_lims.EPPs.files.file_to_udf import csv_well_to_udf
from cg_lims.EPPs.files.hamilton_barcode import make_hamilton_barcode_file
from cg_lims.EPPs.files.make_kapa_csv import make_kapa_csv
from cg_lims.EPPs.files.pooling_map.make_pooling_map import pool_map
from cg_lims.EPPs.files.placement_map.make_96well_placement_map import placement_map


@click.group(invoke_without_command=True)
@click.pass_context
def files(ctx):
    """Main entry point of file commands"""
    pass


files.add_command(make_kapa_csv)
files.add_command(csv_well_to_udf)
files.add_command(pool_map)
files.add_command(placement_map)
files.add_command(make_hamilton_barcode_file)
