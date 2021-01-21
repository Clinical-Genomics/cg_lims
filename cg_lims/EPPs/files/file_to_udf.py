
#!/usr/bin/env python

from cg_lims.exceptions import LimsError, MissingArtifactError
from cg_lims.get.files import get_result_file
from cg_lims import options
from pathlib import Path
from genologics.entities import Artifact
import pandas as pd

import logging
import click
import sys
import math

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
        in_art = Artifact(lims, id=inp['limsid'])
        out_art = Artifact(lims, id=outp['limsid'])
        source_art = in_art if input == True else out_art
        col, row = source_art.location[1].split(':')
        well = col + row
        well_dict[well] = out_art
    return well_dict


def set_udfs(well_field: str, value_field: str, udf: str, well_dict: dict, result_file: Path):
    """Reads the csv and sets the value for each sample"""

    failed_arts = False
    passed_arts = 0
    csv_reader = pd.read_csv(result_file, encoding='latin1')
    data = csv_reader.transpose().to_dict()
    for i, sample in data.items():
        well = sample.get(well_field)
        value = sample.get(value_field)
        if not value or math.isnan(value) or well not in well_dict:
            failed_arts = True
            continue
        art = well_dict[well]
        art.udf[udf] = value
        art.put()
        passed_arts += 1

    if passed_arts< len(well_dict.keys()):
        raise MissingArtifactError(' Some samples in the step were not represented in the file.')
    if failed_arts:
        raise MissingArtifactError(' Some of the samples in the csv file are not represented as samples in the step.')




@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.local_file()
@options.udf()
@options.well_field()
@options.value_field()
@options.input()

@click.pass_context
def csv_well_to_udf(ctx, file, well_field, value_field, udf, input, local_file):
    """Script to copy data from file to udf based on well position
    """
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        well_dict = make_well_dict(process, lims, input)
        file = get_result_file(process=process, file_name=file, file_path=local_file)
        set_udfs(well_field, value_field, udf, well_dict, file)
        click.echo("The file was sucessfully generated.")
    except LimsError as e:
        sys.exit(e.message)
