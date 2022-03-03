#!/usr/bin/env python

import logging
import sys
from typing import List

import click
from genologics.entities import Artifact, Sample
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingArtifactError
from cg_lims.get.artifacts import get_latest_artifact, get_sample_artifact
from cg_lims.get.samples import get_process_samples
from cg_lims.put.queue import queue_artifacts

LOG = logging.getLogger(__name__)


def get_pools_and_samples_to_queue(
    lims: Lims, process_type: List[str], samples: List[Sample]
) -> List[Artifact]:
    """Get samples and pools to place in sequence aggregation.
    Sort of specific script:
    Single arts                                       --> Next Step
    Cust001 - Pools --> split to pools from sort step --> Next Step
    Non RML - Pools --> split in uniq sample arts     --> Next Step

    Args:
        lims: Lims
        rerun_arts: List # Artifacts with Rerun flag
        process_type: List[str] # Name of step(s) before the requeue step
    """

    break_send_to_next_step = False
    send_to_next_step = []
    for sample in samples:
        pool_name = sample.udf.get("pool name")
        if pool_name:
            ## this is a RML - get pools from sort step
            try:
                artifact = get_latest_artifact(lims, sample.id, process_type)
            except MissingArtifactError as e:
                LOG.warning(e.message)
                break_send_to_next_step = True
                continue
        else:
            ## this is a pool (or a sample) and we want to pass its samples to next step
            artifact = get_sample_artifact(lims, sample)
        send_to_next_step.append(artifact)
    if break_send_to_next_step:
        raise MissingArtifactError("Issues getting pools and or samples to queue. See log")
    return list(set(send_to_next_step))


@click.command()
@options.workflow_id(help="Destination workflow id.")
@options.stage_id(help="Destination stage id.")
@options.process_types(
    help="The name(s) of the process type(s) from where we want to fetch the pools"
)
@click.pass_context
def place_samples_in_seq_agg(ctx, workflow_id, stage_id, process_types):
    """Queueing artifacts with given udf==True, to stage in workflow.
    Raising error if quiueing fails."""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    samples = get_process_samples(process)

    try:
        artifacts = get_pools_and_samples_to_queue(lims, process_types, samples)
        queue_artifacts(lims, artifacts, workflow_id, stage_id)
        LOG.info("Artifacts have been queued.")
        click.echo("Artifacts have been queued.")
    except LimsError as e:
        sys.exit(e.message)
