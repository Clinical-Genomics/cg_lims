import logging
from typing import List
from xml.etree.ElementTree import ParseError

from cg_lims.exceptions import MissingSampleError
from genologics.entities import Artifact, Process, Sample

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


def is_negative_control(sample: Sample) -> bool:
    """Check if a given sample is a negative control."""
    try:
        control: str = sample.udf.get("Control")
        if control == "negative":
            return True
        return False
    except ParseError:
        error_message = f"Sample {sample} can't be found in the database."
        LOG.error(error_message)
        raise MissingSampleError(error_message)
