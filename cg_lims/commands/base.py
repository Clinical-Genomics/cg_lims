#!/usr/bin/env python
import click
import yaml
from genologics.lims import Lims

from cg_lims import options

# commands
from cg_lims.EPPs import epps
from cg_lims.scripts.base import scripts
from cg_lims.status_db_api import StatusDBAPI


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
    ctx.obj["arnold_host"] = config_data.get("ARNOLD_HOST")
    ctx.obj["atlas_host"] = config_data.get("ATLAS_HOST")
    ctx.obj["db_uri"] = config_data.get("DB_URI")
    ctx.obj["db_name"] = config_data.get("DB_NAME")


cli.add_command(epps)
cli.add_command(scripts)
