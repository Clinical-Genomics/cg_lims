import logging
import pathlib

import click

from cg_lims import options
from cg_lims.get.files import get_log_content
from cg_lims.scripts.add_sample_meta_data import set_sample_meta_data


@click.group(invoke_without_command=True)
@options.log()
@click.pass_context
def scripts(ctx, log: str):
    """Main entry point of one time script commands"""

    log_path = pathlib.Path(log)

    log_content = get_log_content(ctx.obj["lims"], log)
    if log_content:
        with open(log_path.absolute(), "a") as new_log:
            new_log.write(log_content)

    logging.basicConfig(
        filename=str(log_path.absolute()), filemode="a", level=logging.INFO
    )


scripts.add_command(set_sample_meta_data)
