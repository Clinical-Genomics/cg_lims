#!/usr/bin/env python
from typing import Dict

import click
import yaml
from cg_lims import options
from cg_lims.clients.cg.status_db_api import StatusDBAPI
from cg_lims.clients.cg.token_manager import TokenManager
from cg_lims.clients.smrt_link.models import SmrtLinkConfig

# commands
from cg_lims.EPPs import epps
from cg_lims.scripts.base import scripts
from genologics.lims import Lims


@click.group(invoke_without_command=True)
@options.config()
@click.pass_context
def cli(ctx, config):
    with open(config) as file:
        config_data: Dict = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])

    service_account_email: str = config_data.get("SERVICE_ACCOUNT_EMAIL")
    service_account_auth_file: str = config_data.get("SERVICE_ACCOUNT_AUTH_FILE")
    audience: str = config_data.get("BASEURI")

    token_manager: TokenManager = TokenManager(
        service_account_email=service_account_email,
        service_account_auth_file=service_account_auth_file,
        audience=audience,
    )

    cg_url: str = config_data.get("CG_URL")
    status_db: StatusDBAPI = StatusDBAPI(base_url=cg_url, token_manager=token_manager)

    smrt_link_host: str = config_data.get("SMRT_LINK_HOST")
    smrt_link_user: str = config_data.get("SMRT_LINK_USER")
    smrt_link_pass: str = config_data.get("SMRT_LINK_PASS")
    smrt_link_config: SmrtLinkConfig = SmrtLinkConfig(
        host=smrt_link_host, username=smrt_link_user, password=smrt_link_pass
    )

    ctx.ensure_object(dict)
    ctx.obj["lims"] = lims
    ctx.obj["status_db"] = status_db
    ctx.obj["smrt_link"] = smrt_link_config
    ctx.obj["arnold_host"] = config_data.get("ARNOLD_HOST")
    ctx.obj["atlas_host"] = config_data.get("ATLAS_HOST")
    ctx.obj["db_uri"] = config_data.get("DB_URI")
    ctx.obj["db_name"] = config_data.get("DB_NAME")


cli.add_command(epps)
cli.add_command(scripts)
