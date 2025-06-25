#!/usr/bin/env python

import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import DuplicateSampleError, LimsError, MissingArtifactError
from cg_lims.get.artifacts import (
    filter_artifacts,
    get_artifacts,
    get_latest_analyte,
    get_sample_artifact,
)
from cg_lims.put.queue import queue_artifacts
from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_artifacts_to_requeue(
    lims: Lims,
    rerun_artifacts: List[Artifact],
    process_types: List[str],
    sample_artifact: Optional[bool],
    ignore_fail: bool = False,
) -> List[Artifact]:
    """Get input artifacts to define step (output artifacts of sort step)
    Args:
        lims: Lims
        rerun_artifacts: List # Artifacts with Rerun flag
        process_types: List[str] # Name of step(s) before the requeue step
        sample_artifact: Optional[bool] # Flag to specify if it is the sample artifacts that should be requeued
        ignore_fail: bool # Decides if MissingArtifactErrors should be ignored or not. Default is False.
    """

    if not rerun_artifacts and not ignore_fail:
        raise MissingArtifactError(
            "Found no artifacts to requeue! Please double check the configuration."
        )
    artifacts_to_requeue: List[Artifact] = []
    break_rerun: bool = False
    for artifact in rerun_artifacts:
        representative_sample: Sample = artifact.samples[0]
        try:
            if sample_artifact:
                requeue_art: Artifact = get_sample_artifact(lims=lims, sample=representative_sample)
            else:
                requeue_art: Artifact = get_latest_analyte(
                    lims=lims, sample_id=representative_sample.id, process_types=process_types
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
            f"Warning same sample in many pools: {' ,'.join([sample.id for sample in duplicate_samples])}"
        )


def queue_rerun_artifacts(
    lims: Lims,
    artifacts: List[Artifact],
    workflow_id: str,
    stage_id: str,
    ignore_fail: bool = False,
) -> None:
    """Queue artifacts for rerun. Ignores missing artifacts if 'ignore_failed' is True."""
    try:
        queue_artifacts(lims=lims, artifacts=artifacts, workflow_id=workflow_id, stage_id=stage_id)
    except MissingArtifactError as e:
        if not ignore_fail:
            raise e


@click.command()
@options.workflow_id(help="Destination workflow id.")
@options.stage_id(help="Destination stage id.")
@options.process_types(
    help="The name(s) of the process type(s) before the requeue step. "
    "Fetching artifact to requeue from here if specified."
)
@options.sample_artifact(help="Use this flag to queue the sample artifacts for a sample.")
@options.udf(help="UDF that will tell which artifacts to move.")
@options.input(
    help="Use this flag if you want to queue the input artifacts of the current process. Default is to queue the "
    "output artifacts (analytes) of the process. "
)
@options.ignore_fail(
    help="Use this flag if you don't want to warn about missing samples to requeue."
)
@click.pass_context
def rerun_samples(
    ctx,
    workflow_id: str,
    stage_id: str,
    process_types: List[str],
    sample_artifact: Optional[bool],
    udf: str,
    input: bool,
    ignore_fail: Optional[bool],
):
    """Script to requeue samples for sequencing."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]

    artifacts: List[Artifact] = get_artifacts(process=process, input=input)
    rerun_artifacts: List[Artifact] = filter_artifacts(artifacts=artifacts, udf=udf, value=True)
    try:
        artifacts_to_requeue: List[Artifact] = get_artifacts_to_requeue(
            lims=lims,
            rerun_artifacts=rerun_artifacts,
            process_types=process_types,
            sample_artifact=sample_artifact,
            ignore_fail=ignore_fail,
        )
        check_same_sample_in_many_rerun_pools(rerun_arts=artifacts_to_requeue)
        queue_rerun_artifacts(
            lims=lims,
            artifacts=artifacts_to_requeue,
            workflow_id=workflow_id,
            stage_id=stage_id,
            ignore_fail=ignore_fail,
        )
        click.echo("Artifacts have been queued.")
    except LimsError as e:
        sys.exit(e.message)
