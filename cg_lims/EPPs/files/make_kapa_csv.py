#!/usr/bin/env python

from cg_lims.get.artifacts import get_artifacts, get_latest_artifact
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.make_csv import make_plate_file
from cg_lims import options
from genologics.lims import Lims
from genologics.entities import Process

import string
import logging
import click
import sys

LOG = logging.getLogger(__name__)


MINIMUM_AMOUNT = 10


def get_ligation_master_mix(amount):
    """Two different master mixes are used, A and B. 
    Master mix B has less volume of "xGen CS Adapter-Tech Access" 
    and is used for samples with DNA amount <25 ng.
    """

    if amount < 25:
        return 'B'
    else:
        return 'A'


def get_pcr_plate(amount):
    """Depending on amount of DNA the samples are run with different number 
    of PCR-cycles. These are run in three different PCR-plates. 
    The script sets the PCR-plate.
    """

    if amount < 50:
        plate = 'Plate3'
    elif amount < 200:
        plate = 'Plate2'
    else:
        plate = 'Plate1'
    return plate


def get_index_well(art):
    """Parsing out the index well position from the reagent label string wich 
    typically looks like this: 'A05 IDT_10nt_446 (AGCGTGACCT-CCATCCGAGT)'
    """

    if art.reagent_labels:
        # Assuming one reagent label per artifact (reagent_labels is a list):
        reagent_label = art.reagent_labels[0]

        # Getting the index well:
        index_well_with_zero = reagent_label.split(" ")[0]

        # Picking out column and removing zeros by int():
        index_well_col = int(index_well_with_zero[1:])
        index_well_row = index_well_with_zero[0]
        index_well = f"{index_well_row}{index_well_col}"
    else:
        index_well = "-"
    return index_well


def get_file_data_and_write(lims: Lims, amount_step: str, artifacts: list, file: str) -> dict:
    """Getting row data for hamilton file based on amount and reagent label"""

    failed_samples = []
    file_rows = {}
    for art in artifacts:
        sample_id = art.samples[0].id
        index_well = get_index_well(art)
        well = art.location[1].replace(":", "")
        amount_artifact = get_latest_artifact(lims, sample_id, amount_step)
        amount = amount_artifact.udf.get("Amount needed (ng)")

        if not amount:
            failed_samples.append(sample_id)
            continue

        if amount <= MINIMUM_AMOUNT:
            amount = MINIMUM_AMOUNT

        ligation_master_mix = get_ligation_master_mix(amount)
        pcr_plate = get_pcr_plate(amount)

        file_rows[well] = [
            sample_id,
            well,
            ligation_master_mix,
            index_well,
            pcr_plate,
        ]
        art.udf["Ligation Master Mix"] = ligation_master_mix
        art.udf["PCR Plate"] = pcr_plate
        art.put()

    headers = [
        "LIMS ID",
        "Sample Well",
        "Ligation Master Mix",
        "Index Well",
        "PCR Plate",
    ]

    make_plate_file(file, file_rows, headers)

    if failed_samples:
        raise MissingUDFsError(
            f"Could not find udf: Amount needed (ng) for samples: {', '.join(failed_samples)}, from step {amount_step}."
        )


@click.command()
@options.process_type(help="Amount step name.")
@options.file_placeholder(help="Hamilton file.")
@click.pass_context
def make_kapa_csv(ctx, file, process_type):
    """Script to make a csv file for hamilton. See AM doc #2125
    """
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    artifacts = get_artifacts(process=process, input=False)

    file_name = f"{file}_{artifacts[0].container.name}_{process.type.name.replace(' ', '_')}"

    try:
        get_file_data_and_write(lims, process_type, artifacts, file_name)
        click.echo("The file was sucessfully generated.")
    except LimsError as e:
        sys.exit(e.message)
