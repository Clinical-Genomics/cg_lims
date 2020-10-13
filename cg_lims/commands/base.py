#!/usr/bin/env python
from cg_lims.get.files import get_lims_log_file
from cg_lims import options

from genologics.lims import Lims

from genologics.entities import Process

import pathlib
import logging
import click
import yaml

# commands
from cg_lims.EPPs.move.rerun_samples import rerun_samples
from cg_lims.EPPs.move.move_samples import move_samples
from cg_lims.EPPs.move.place_samples_in_seq_agg import place_samples_in_seq_agg
from cg_lims.EPPs.files.make_kapa_csv import make_kapa_csv
from cg_lims.EPPs.get_and_set.art2samp import art2samp


@click.group(invoke_without_command=True)
@options.log()
@options.process()
@options.config()
@click.pass_context
def cli(ctx, log, process, config):

    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(
        config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"]
    )

    log_path = pathlib.Path(log)
    if not log_path.is_file():
        log_path = get_lims_log_file(lims, log)
    logging.basicConfig(
        filename=str(log_path.absolute()), filemode="a", level=logging.INFO
    )
    process = Process(lims, id=process)
    ctx.ensure_object(dict)
    ctx.obj["lims"] = lims
    ctx.obj["process"] = process


cli.add_command(rerun_samples)
cli.add_command(move_samples)
cli.add_command(place_samples_in_seq_agg)
cli.add_command(make_kapa_csv)
cli.add_command(art2samp)
