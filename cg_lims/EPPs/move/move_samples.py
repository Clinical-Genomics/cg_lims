#!/usr/bin/env python

import logging
import sys

import click
from genologics.entities import Process
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import filter_artifacts, get_artifacts
from cg_lims.put.queue import queue_artifacts

LOG = logging.getLogger(__name__)


@click.command()
@options.workflow_id(help="Destination workflow id.")
@options.stage_id(help="Destination stage id.")
@options.udf(help="UDF that will tell wich artifacts to move.")
@options.input(
    help="Use this flag if you want to queue the input artifacts of the current process. Default is to queue the output artifacts (analytes) of the process."
)
@click.pass_context
def move_samples(ctx, workflow_id: str, stage_id: str, udf: str, input: bool):
    """Script to move aritfats to another stage.

    Queueing artifacts with <udf==True>, to stage with <stage-id>
    in workflow with <workflow-id>. Raising error if quiueing fails."""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    artifacts = get_artifacts(process=process, input=input)
    filtered_artifacts = filter_artifacts(artifacts, udf, True)

    if not filtered_artifacts:
        LOG.info(f"No artifacts to queue.")
        return

    try:
        queue_artifacts(lims, filtered_artifacts, workflow_id, stage_id)
        click.echo("Artifacts have been queued.")
    except LimsError as e:
        sys.exit(e.message)
