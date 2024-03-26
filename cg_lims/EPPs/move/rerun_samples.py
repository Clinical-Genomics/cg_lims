#!/usr/bin/env python

import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import DuplicateSampleError, LimsError, MissingArtifactError
from cg_lims.get.artifacts import filter_artifacts, get_artifacts, get_latest_analyte
from cg_lims.put.queue import queue_artifacts
from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_artifacts_to_requeue(
    lims: Lims, rerun_artifacts: List[Artifact], process_types: List[str]
) -> List[Artifact]:
    """Get input artifacts to define step (output artifacts of sort step)
    Args:
        lims: Lims
        rerun_artifacts: List # Artifacts with Rerun flag
        process_types: List[str] # Name of step(s) before the requeue step
    """

    artifacts_to_requeue: List[Artifact] = []
    break_rerun: bool = False
    for artifact in rerun_artifacts:
        representative_sample_id: str = artifact.samples[0].id
        try:
            requeue_art: Artifact = get_latest_analyte(
                lims=lims, sample_id=representative_sample_id, process_types=process_types
            )
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

    all_samples: List[Sample] = []

    for art in rerun_arts:
        all_samples += art.samples
    for s in set(all_samples):
        all_samples.remove(s)
    duplicate_samples: List[Sample] = list(set(all_samples))
    if duplicate_samples:
        raise DuplicateSampleError(
            f"Waring same sample in many pools: {' ,'.join([sample.id for sample in duplicate_samples])}"
        )


@click.command()
@options.workflow_id(help="Destination workflow id.")
@options.stage_id(help="Destination stage id.")
@options.process_types(
    help="The name(s) of the process type(s) before the requeue step. Fetching artifact to requeue from here."
)
@options.udf(help="UDF that will tell wich artifacts to move.")
@options.input(
    help="Use this flag if you want to queue the input artifacts of the current process. Default is to queue the "
    "output artifacts (analytes) of the process. "
)
@click.pass_context
def rerun_samples(
    ctx, workflow_id: str, stage_id: str, process_types: List[str], udf: str, input: bool
):
    """Script to requeue samples for sequencing."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]

    artifacts: List[Artifact] = get_artifacts(process=process, input=input)
    rerun_artifacts: List[Artifact] = filter_artifacts(artifacts=artifacts, udf=udf, value=True)
    if rerun_artifacts:
        try:
            artifacts_to_requeue: List[Artifact] = get_artifacts_to_requeue(
                lims=lims, rerun_artifacts=rerun_artifacts, process_types=process_types
            )
            check_same_sample_in_many_rerun_pools(artifacts_to_requeue)
            queue_artifacts(lims, artifacts_to_requeue, workflow_id, stage_id)
            click.echo("Artifacts have been queued.")
        except LimsError as e:
            sys.exit(e.message)
