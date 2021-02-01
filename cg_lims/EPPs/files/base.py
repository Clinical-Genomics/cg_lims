#!/usr/bin/env python

import click

from cg_lims.EPPs.files.file_to_udf import csv_well_to_udf

# commands
from cg_lims.EPPs.files.make_kapa_csv import make_kapa_csv


@click.group(invoke_without_command=True)
@click.pass_context
def files(ctx):
    """Main entry point of file commands"""
    pass


files.add_command(make_kapa_csv)
files.add_command(csv_well_to_udf)
