from genologics.entities import Process, Sample, Artifact
from cg_lims.exceptions import MissingSampleError
from typing import List



def get_process_samples(process: Process) -> List[Sample]:
    """Get all samples in a process"""

    all_samples = []
    for art in process.all_inputs():
        all_samples += art.samples

    return list(set(all_samples))

def get_artifact_sample(artifact: Artifact)-> Sample:
    """Checking that a artifact has one and only one sample.
    Returning the sample if it exists.
    Raising MissingSampleError otherwise."""
    
    try:
        samples = artifact.samples
    except:
        raise MissingSampleError(f"Artifact {artifact.id} has no samples.")
    if not samples:
        raise MissingSampleError(f"Artifact {artifact.id} has no samples.")
    elif len(samples) > 1:
        raise MissingSampleError(f"Artifact {artifact.id} has more than one sample.")

    return samples[0]
