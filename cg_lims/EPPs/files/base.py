#!/usr/bin/env python
import click
from cg_lims.EPPs.files.barcode_tubes import make_barcode_csv
from cg_lims.EPPs.files.csv_for_kapa_truble_shooting.csv_for_kapa_debug import trouble_shoot_kapa

# commands
from cg_lims.EPPs.files.file_to_udf import csv_well_to_udf
from cg_lims.EPPs.files.hamilton.base import hamilton
from cg_lims.EPPs.files.ont_json_to_udf import parse_ont_report
from cg_lims.EPPs.files.placement_map.make_96well_placement_map import placement_map
from cg_lims.EPPs.files.pooling_map.make_pooling_map import pool_map
from cg_lims.EPPs.files.sample_sheet.create_ont_sample_sheet import create_ont_sample_sheet
from cg_lims.EPPs.files.sample_sheet.create_sample_sheet import create_sample_sheet
from cg_lims.EPPs.files.smrt_link.run_design import create_smrtlink_run_design
from cg_lims.EPPs.files.smrt_link.sample_setup import create_smrtlink_sample_setup
from cg_lims.EPPs.files.xml_to_udf import parse_run_parameters
from cg_lims.EPPs.files.femtopulse_csv import make_femtopulse_csv


@click.group(invoke_without_command=True)
@click.pass_context
def files(ctx):
    """Main entry point of file commands"""
    pass


files.add_command(csv_well_to_udf)
files.add_command(pool_map)
files.add_command(placement_map)
files.add_command(hamilton)
files.add_command(trouble_shoot_kapa)
files.add_command(make_barcode_csv)
files.add_command(create_ont_sample_sheet)
files.add_command(create_sample_sheet)
files.add_command(parse_run_parameters)
files.add_command(parse_ont_report)
files.add_command(make_femtopulse_csv)
files.add_command(create_smrtlink_sample_setup)
files.add_command(create_smrtlink_run_design)
