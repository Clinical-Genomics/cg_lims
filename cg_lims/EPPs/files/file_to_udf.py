#!/usr/bin/env python

import logging
import sys
import csv
from pathlib import Path

import click
from genologics.entities import Artifact

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingFileError
from cg_lims.get.artifacts import get_artifact_by_name
from cg_lims.get.files import get_file_path

LOG = logging.getLogger(__name__)


def make_well_dict(process, lims, input):
    """Creates a well dict based on input_output_map
    keys: well of input artifact
    values: input/output artifact depending on the input flag
    """

    well_dict = {}
    for inp, outp in process.input_output_maps:
        if outp.get("output-generation-type") == "PerAllInputs":
            continue
        in_art = Artifact(lims, id=inp["limsid"])
        out_art = Artifact(lims, id=outp["limsid"])
        source_art = in_art if input == True else out_art
        col, row = source_art.location[1].split(":")
        well = col + row
        well_dict[well] = out_art
    return well_dict


def set_udfs(well_field: str, value_field: str, udf: str, well_dict: dict, result_file: Path):
    """Reads the csv and sets the value for each sample"""

    error_msg = []
    passed_arts = 0
    with open(result_file, newline="", encoding="latin1") as csvfile:
        reader = csv.DictReader(csvfile)
        for sample in reader:
            well = sample.get(well_field)
            value = sample.get(value_field)
            if value is None:
                error_msg.append("Some samples in the file hade missing values.")
                continue
            elif well not in well_dict:
                error_msg.append("Some samples in the step were not represented in the file.")
                continue
            art = well_dict[well]
            try:
            	art.udf[udf] = str(value)
            except:
                art.udf[udf] = float(value)
            art.put()
            passed_arts += 1

    if passed_arts < len(well_dict.keys()):
        error_msg.append("Some samples in the step were not represented in the file.")

    error_string = ' '.join(list(set(error_msg)))
    if error_msg:
        raise MissingArtifactError(error_string)


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.local_file()
@options.udf()
@options.well_field()
@options.value_field()
@options.input()
@click.pass_context
def csv_well_to_udf(
    ctx, file: str, well_field: str, value_field: str, udf: str, input: bool, local_file: str
):
    """Script to copy data from file to udf based on well position"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    if local_file:
        file_path = local_file
    else:
        file_art = get_artifact_by_name(process=process, name=file)
        file_path = get_file_path(file_art)

    try:
        if not Path(file_path).is_file():
            raise MissingFileError(f"No such file: {file_path}")
        well_dict = make_well_dict(process, lims, input)
        set_udfs(well_field, value_field, udf, well_dict, file_path)
        click.echo("The udfs were sucessfully populated.")
    except LimsError as e:
        sys.exit(e.message)
