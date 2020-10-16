#!/usr/bin/env python
from cg_lims import options

from genologics.lims import Lims

import click
import yaml

# commands
from cg_lims.EPPs import epps


@click.group(invoke_without_command=True)
@options.config()
@click.pass_context
def cli(ctx, config):

    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(
        config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"]
    )

    ctx.ensure_object(dict)
    ctx.obj["lims"] = lims


cli.add_command(epps)
