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
from cg_lims.EPPs import epps

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


cli.add_command(epps)
