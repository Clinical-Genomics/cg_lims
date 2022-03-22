#!/usr/bin/env python
import logging
import pathlib

import click
from cg_lims import options

# commands
from .check_config import check_config
from .prepare_fixture import make_fixure
from .one_time_scripts.base import one_time


@click.group(invoke_without_command=True)
@options.log()
@click.pass_context
def scripts(ctx, log: str):
    """Main entry point to run scripts"""

    log_path = pathlib.Path(log)
    logging.basicConfig(filename=str(log_path.absolute()), filemode="a", level=logging.INFO)


scripts.add_command(check_config)
scripts.add_command(make_fixure)
scripts.add_command(one_time)
