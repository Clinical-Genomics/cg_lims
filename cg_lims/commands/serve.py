import click
import logging
import uvicorn

from cg_lims.models.context import APIContextObject

LOG = logging.getLogger(__name__)


@click.command("serve")
@click.option("--reload", is_flag=True)
@click.pass_context
def serve_command(ctx, reload: bool):
    """Serve the Statina app for testing purpose.
    This command will serve the user interface (external) as default
    """
    api_context = APIContextObject(**ctx.obj)
    LOG.info("Running api on host:%s and port:%s", api_context.host, api_context.port)
    uvicorn.run(
        app="cg_lims.app.api.api_v1.api:app",
        host=api_context.host,
        port=api_context.port,
        reload=reload,
    )
