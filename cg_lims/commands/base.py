#!/usr/bin/env python
from cg_lims.get.files import get_lims_log_file
from cg_lims import options

from genologics.lims import Lims
from genologics.config import BASEURI, USERNAME, PASSWORD
from genologics.entities import Process

import pathlib
import logging
import click

# commands
from cg_lims.EPPs.move.rerun_samples import rerun_samples
from cg_lims.EPPs.move.move_samples import move_samples
from cg_lims.EPPs.move.place_samples_in_seq_agg import place_samples_in_seq_agg



@click.group()
@options.log()
@options.process()
@click.pass_context
def cli(ctx, log, process):
    lims = Lims(BASEURI, USERNAME, PASSWORD)
    log_path = pathlib.Path(log)
    if not log_path.is_file():
       log_path = get_lims_log_file(lims, log)
    logging.basicConfig(filename = str(log_path.absolute()), filemode='a', level=logging.INFO)
    process = Process(lims, id=process)
    ctx.ensure_object(dict)
    ctx.obj['lims'] = lims
    ctx.obj['process'] = process

cli.add_command(rerun_samples)
cli.add_command(move_samples)
cli.add_command(place_samples_in_seq_agg)

