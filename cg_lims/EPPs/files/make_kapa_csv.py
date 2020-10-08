#!/usr/bin/env python

from cg_lims.get.artifacts import get_artifacts, get_latest_artifact
from cg_lims import options
from genologics.lims import Lims
from genologics.entities import Process

import string
import logging
import click
import csv
LOG = logging.getLogger(__name__)


def get_file_rows(lims: Lims, amount_step: str, artifacts: list)-> dict:
    """Getting row data for hamilton file based on amount, reagent label and well."""

    translate_amount = {10: {'Ligation Master Mix':'B', 'PCR Plate': 'Plate3'},
                        50: {'Ligation Master Mix':'A', 'PCR Plate': 'Plate2'},
                        250: {'Ligation Master Mix':'A', 'PCR Plate': 'Plate1'}}

    file_rows ={} 
    for art in artifacts:
        sample_id = art.samples[0].id
        if art.reagent_labels:
            reagent_label = art.reagent_labels[0]
            index_well_col = str(int(reagent_label.split(' ')[0][1:3]))
            index_well_row = reagent_label.split(' ')[0][0]
            index_well = index_well_row + index_well_col
        else:
            index_well = '-'
        well = art.location[1].replace(':','')
        amount_artifact = get_latest_artifact(lims, sample_id, amount_step)
        amount = amount_artifact.udf.get('Amount needed (ng)')
        if amount<=10:
            amount=10
        mix_plate = translate_amount.get(amount)
        if mix_plate:
            file_rows[well] = [sample_id ,well ,mix_plate['Ligation Master Mix'],index_well ,mix_plate['PCR Plate']]
            art.udf['Ligation Master Mix'] = mix_plate['Ligation Master Mix']
            art.udf['PCR Plate'] = mix_plate['PCR Plate']
            art.put()
        else:
            failed_samples.append(sample_id)
    return file_rows


def make_file(hamilton_file: str, file_rows: dict):
    """Creating a hamilton file"""

    hamilton_file = f"{hamilton_file}_KAPA_Hamilton.txt"
    hamilton_csv = open( hamilton_file , 'w')
    wr = csv.writer(hamilton_csv)
    wr.writerow(['LIMS ID', 'Sample Well', 'Ligation Master Mix', 'Index Well', 'PCR Plate'])
    for col in range(1,13):
        for row in string.ascii_uppercase[0:8]:
            row = file_rows.get(f"{row}{col}")
            if row:
                wr.writerow(row)


@click.command()
@options.process_type(help="Amount step name.")
@options.file_placeholder(help="Hamilton file.")
@click.pass_context
def make_kapa_csv(ctx, file, process_type):
    """Script to make a csv file for hamilton."""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    artifacts = get_artifacts(process=process, input=False)
    file_rows = get_file_rows(lims, process_type, artifacts)
    make_file(file, file_rows)

