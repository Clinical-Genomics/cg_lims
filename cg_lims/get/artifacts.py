from genologics.entities import Process, Artifact, Sample
from genologics.lims import Lims

from operator import attrgetter
from typing import List


from cg_lims.exceptions import QueueArtifactsError, MissingArtifactError



def get_sample_artifact(lims: Lims, sample: Sample) -> Artifact:
    """Returning the initial artifact related to a sample.
    Assuming first artifact is allways named sample.id + 'PA1."""

    return Artifact(lims, id=f"{sample.id}PA1")


def get_artifacts(process: Process, input: bool) -> List[Artifact]:
    """If inputs is True, returning all input analytes of the process,
    otherwise returning all output analytes of the process"""

    if input:
        artifacts = process.all_inputs(unique=True)
    else:
        artifacts = [a for a in process.all_outputs(unique=True) if a.type == "Analyte"]
    return artifacts


def filter_artifacts(artifacts: List[Artifact], udf: str, value) -> List[Artifact]:
    """Returning a list of only artifacts with udf==value"""

    return [a for a in artifacts if a.udf.get(udf) == value]


def get_latest_artifact(lims: Lims, sample_id: str, process_type: List[str]) -> Artifact:
    """Getting the most recently generated artifact by process_type and sample_id.

    Searching for all artifacts (Analytes) associated with <sample_id> that
    were produced by <process_type>. 
    
    Returning the artifact with latest parent_process.date_run. 
    If there are many such artifacts only one will be returned."""

    artifacts = lims.get_artifacts(
        samplelimsid=sample_id,
        type="Analyte",
        process_type=process_type,
    )
    if not artifacts:
        raise MissingArtifactError(
            message=f"Could not find a artifact with sample: {sample_id} generated by process: {' ,'.join(process_type)}"
        )
    
    artifacts = [(a.parent_process.date_run, a) for a in artifacts]
    artifacts.sort()
    date, latest_art = artifacts[-1]

    return latest_art



