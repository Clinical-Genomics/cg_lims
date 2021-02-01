#!/usr/bin/env python
import click
import yaml
from genologics.lims import Lims

from cg_lims import options
from cg_lims.cgface_api import CgFace

# commands
from cg_lims.EPPs import epps


@click.group(invoke_without_command=True)
@options.config()
@click.pass_context
def cli(ctx, config):
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])
    cgface = CgFace(config_data["CG_URL"])

    ctx.ensure_object(dict)
    ctx.obj["lims"] = lims
    ctx.obj["cgface"] = cgface


cli.add_command(epps)
