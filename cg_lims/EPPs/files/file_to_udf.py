#!/usr/bin/env python

import csv
import logging
import sys
from pathlib import Path

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingFileError, ArgumentError
from cg_lims.get.artifacts import get_artifact_by_name
from cg_lims.get.files import get_file_path
from genologics.entities import Artifact

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


def set_udfs(well_field: str, udf_vf_dict: dict, well_dict: dict, result_file: Path):
    """Reads the csv and sets the value for each sample"""

    error_msg = []
    passed_arts = 0
    with open(result_file, newline="", encoding="latin1") as csvfile:
        reader = csv.DictReader(csvfile)
        for sample in reader:
            well = sample.get(well_field)


            
            value = sample.get(value_field)
            if value is None:
                error_msg.append("Some samples in the file had missing values.")
                LOG.info(f"Missing value for sample {sample} in well {well}. Skipping!")
                continue
            elif well not in well_dict:
                LOG.info(f"Well {well} was not found in the step. Skipping!")
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

    error_string = " ".join(list(set(error_msg)))
    if error_msg:
        raise MissingArtifactError(error_string)


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.local_file()
@options.udf_values()
@options.well_field()
@options.value_fields()
@options.input()
@click.pass_context
def csv_well_to_udf(
    ctx, file: str, well_field: str, value_fields: tuple, udf_values: tuple, input: bool, local_file: str
):
    """Script to copy data from file to udf based on well position"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    if len(udf_values) != len(value_fields):
        raise ArgumentError(f"The number of artifact-udfs to update and file value fields must be the same.")

    udf_vf_dict: dict = {}
    for i in range(len(udf_values)):
        udf_vf_dict[udf_values[i]] = value_fields[i]

    if local_file:
        file_path = local_file
    else:
        file_art = get_artifact_by_name(process=process, name=file)
        file_path = get_file_path(file_art)

    try:
        if not Path(file_path).is_file():
            raise MissingFileError(f"No such file: {file_path}")
        well_dict = make_well_dict(process, lims, input)
        set_udfs(well_field, udf_vf_dict, well_dict, file_path)
        click.echo("The udfs were sucessfully populated.")
    except LimsError as e:
        sys.exit(e.message)
