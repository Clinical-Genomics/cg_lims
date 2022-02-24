from typing import List

from genologics.entities import Artifact, Process, Sample

from cg_lims.exceptions import MissingSampleError
import logging

LOG = logging.getLogger(__name__)


def get_process_samples(process: Process) -> List[Sample]:
    """Get all samples in a process"""

    all_samples = []
    for art in process.all_inputs():
        all_samples += art.samples

    return list(set(all_samples))


def get_one_sample_from_artifact(artifact: Artifact) -> Sample:
    """Checking that an artifact has one and only one sample.
    Returning the sample if it exists.
    Raising MissingSampleError otherwise."""

    no_samples_message = f"Artifact {artifact.id} has no samples."
    more_than_one_message = f"Artifact {artifact.id} has more than one sample."
    try:
        samples = artifact.samples
    except:
        LOG.error(no_samples_message)
        raise MissingSampleError(message=no_samples_message)
    if not samples:
        LOG.error(no_samples_message)
        raise MissingSampleError(message=no_samples_message)
    elif len(samples) > 1:
        LOG.error(more_than_one_message)
        raise MissingSampleError(message=more_than_one_message)

    return samples[0]
