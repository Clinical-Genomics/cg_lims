#!/usr/bin/env python
from cg_lims import options
from cg_lims.get.files import get_log_content

import click
import logging
import pathlib

from genologics.entities import Process


# commands
from cg_lims.EPPs.move import move
from cg_lims.EPPs.files import files
from cg_lims.EPPs.udf import udf


@click.group(invoke_without_command=True)
@options.log()
@options.process()
@click.pass_context
def epps(ctx, log: str, process: Process):
    """Main entry point of epp commands"""

    log_path = pathlib.Path(log)

    log_content = get_log_content(ctx.obj['lims'], log)
    if log_content:
        with open(log_path.absolute(), 'a') as new_log:
            new_log.write(log_content)

    logging.basicConfig(
        filename=str(log_path.absolute()), filemode="a", level=logging.INFO
    )
    process = Process(ctx.obj['lims'], id=process)
    ctx.obj["process"] = process


epps.add_command(move)
epps.add_command(files)
epps.add_command(udf)
