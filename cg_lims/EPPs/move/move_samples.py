#!/usr/bin/env python

import logging
import sys
from typing import Optional

import click

from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import filter_artifacts, get_artifacts
from cg_lims.put.queue import queue_artifacts

LOG = logging.getLogger(__name__)


@click.command()
@options.workflow_id(help="Destination workflow id.")
@options.stage_id(help="Destination stage id.")
@options.udf(help="UDF that will tell which artifacts to move.")
@options.input(
    help="Use this flag if you want to queue the input artifacts of the current process. Default is to queue the "
    "output artifacts (analytes) of the process. "
)
@click.pass_context
def move_samples(ctx, workflow_id: str, stage_id: str, udf: Optional[str], input: bool):
    """Script to move aritfats to another stage.

    Queueing artifacts from the current process with <udf>==True, to stage with <stage-id>
    in workflow with <workflow-id>. Raising error if queuing fails.

    If udf is None all artifacts from the current step will be queued."""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    artifacts = get_artifacts(process=process, input=input)
    filtered_artifacts = filter_artifacts(artifacts, udf, True)

    if not filtered_artifacts:
        LOG.info("No artifacts to queue.")
        return

    try:
        queue_artifacts(lims, filtered_artifacts, workflow_id, stage_id)
        click.echo("Artifacts have been queued.")
    except LimsError as e:
        sys.exit(e.message)
