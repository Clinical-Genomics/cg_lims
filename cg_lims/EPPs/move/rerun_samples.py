#!/usr/bin/env python

import logging
import sys
from typing import List

import click
from genologics.entities import Artifact, Process, Stage
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import DuplicateSampleError, LimsError, MissingArtifactError
from cg_lims.get.artifacts import filter_artifacts, get_artifacts, get_latest_artifact
from cg_lims.put.queue import queue_artifacts

LOG = logging.getLogger(__name__)


def get_artifacts_to_requeue(
    lims: Lims, rerun_arts: List[Artifact], process_type: List[str]
) -> List[Artifact]:
    """Get input artifacts to define step (output artifacts of sort step)
    Args:
        lims: Lims
        rerun_arts: List # Artifacts with Rerun flag
        process_type: List[str] # Name of step(s) before the requeue step
    """

    artifacts_to_requeue = []
    break_rerun = False
    for art in rerun_arts:
        representative_sample_id = art.samples[0].id  ## hantera med if samples..
        try:
            requeue_art = get_latest_artifact(lims, representative_sample_id, process_type)
        except MissingArtifactError as e:
            LOG.warning(e.message)
            break_rerun = True
            continue
        artifacts_to_requeue.append(requeue_art)
    if break_rerun:
        raise MissingArtifactError("Issues finding artifacts to requeue. See log")
    return list(set(artifacts_to_requeue))


def check_same_sample_in_many_rerun_pools(rerun_arts: List[Artifact]) -> None:
    """Check that the same sample does not occure in more than one of the pools to rerun."""

    all_samples = []

    for art in rerun_arts:
        all_samples += art.samples
    for s in set(all_samples):
        all_samples.remove(s)
    duplicate_samples = list(set(all_samples))
    if duplicate_samples:
        raise DuplicateSampleError(
            f"Waring same sample in many pools: {' ,'.join([sample.id for sample in duplicate_samples])}"
        )


@click.command()
@options.workflow_id(help="Destination workflow id.")
@options.stage_id(help="Destination stage id.")
@options.process_type(
    help="The name(s) of the process type(s) before the requeue step. Fetching artifact to requeue from here."
)
@options.udf(help="UDF that will tell wich artifacts to move.")
@click.pass_context
def rerun_samples(ctx, workflow_id, stage_id, udf, process_type):
    """Script to requeue samples for sequencing."""
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    artifacts = get_artifacts(process, False)
    rerun_arts = filter_artifacts(artifacts, udf, True)
    if rerun_arts:
        try:
            artifacts_to_requeue = get_artifacts_to_requeue(lims, rerun_arts, process_type)
            check_same_sample_in_many_rerun_pools(artifacts_to_requeue)
            queue_artifacts(lims, artifacts_to_requeue, workflow_id, stage_id)
            click.echo("Artifacts have been queued.")
        except LimsError as e:
            sys.exit(e.message)
