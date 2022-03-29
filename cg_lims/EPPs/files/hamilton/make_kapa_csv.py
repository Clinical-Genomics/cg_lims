#!/usr/bin/env python

import logging
import sys

import click
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.manage_csv_files import make_plate_file
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte
from cg_lims.get.fields import get_index_well

LOG = logging.getLogger(__name__)


MINIMUM_AMOUNT = 10


def get_ligation_master_mix(amount):
    """Two different master mixes are used, A and B.
    Master mix B has less volume of "xGen CS Adapter-Tech Access"
    and is used for samples with DNA amount <25 ng.
    """

    if amount < 25:
        return "B"
    else:
        return "A"


def get_pcr_plate(amount):
    """Depending on amount of DNA the samples are run with different number
    of PCR-cycles. These are run in three different PCR-plates.
    The script sets the PCR-plate.
    """

    if amount < 50:
        return "Plate3"
    elif amount < 200:
        return "Plate2"
    else:
        return "Plate1"


def get_file_data_and_write(lims: Lims, amount_step: str, artifacts: list, file: str) -> dict:
    """Getting row data for hamilton file based on amount and reagent label"""

    failed_samples = []
    file_rows = {}
    for art in artifacts:
        sample_id = art.samples[0].id
        index_well = get_index_well(art)
        well = art.location[1].replace(":", "")
        amount_artifact = get_latest_analyte(lims, sample_id, amount_step)
        amount = amount_artifact.udf.get("Amount needed (ng)")

        if not amount:
            failed_samples.append(sample_id)
            continue

        amount = max(amount, MINIMUM_AMOUNT)

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


def resolve_file_extension(extension: str) -> str:
    """Appends a period symbol to extension string if none is present. Otherwise, returns given extension string"""
    if extension:
        if extension.startswith("."):
            return extension
        return f".{extension}"
    return ""


@click.command()
@options.process_types(help="Amount step name.")
@options.file_placeholder(help="Hamilton file.")
@options.file_extension()
@click.pass_context
def make_kapa_csv(ctx: click.Context, file: str, extension: str, process_types: str):
    """Script to make a csv file for hamilton. See AM doc #2125"""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    artifacts = get_artifacts(process=process, input=False)

    file_name = (
        f"{file}_{artifacts[0].container.name}_{process.type.name.replace(' ', '_')}"
        f"{resolve_file_extension(extension)}"
    )

    try:
        get_file_data_and_write(lims, process_types, artifacts, file_name)
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
