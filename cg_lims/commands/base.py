#!/usr/bin/env python
import click
import yaml
from genologics.lims import Lims

from cg_lims import options
from cg_lims.status_db_api import StatusDBAPI

# commands
from cg_lims.EPPs import epps
from cg_lims.commands.serve import serve_command


@click.group(invoke_without_command=True)
@options.config()
@click.pass_context
def cli(ctx, config):
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])
    status_db = StatusDBAPI(config_data["CG_URL"])

    ctx.ensure_object(dict)
    ctx.obj["lims"] = lims
    ctx.obj["status_db"] = status_db
    ctx.obj["host"] = config_data.get("CG_LIMS_HOST")
    ctx.obj["port"] = config_data.get("CG_LIMS_PORT")


cli.add_command(epps)
cli.add_command(serve_command)
