from operator import attrgetter
from typing import List, Optional

from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

from cg_lims.exceptions import FileError, MissingArtifactError
from datetime import datetime


def get_sample_artifact(lims: Lims, sample: Sample) -> Artifact:
    """Returning the initial artifact related to a sample.
    Assuming first artifact is allways named sample.id + 'PA1."""

    return Artifact(lims, id=f"{sample.id}PA1")


def get_qc_output_artifacts(lims: Lims, process: Process) -> List[Artifact]:
    """Get output 'artifacts' (messuements) of a qc process"""

    input_output_maps = process.input_output_maps
    artifact_ids = [
        io[1]["limsid"] for io in input_output_maps if io[1]["output-generation-type"] == "PerInput"
    ]
    return [Artifact(lims, id=id) for id in artifact_ids if id is not None]


def get_artifacts(
    process: Process, input: Optional[bool] = False, measurement: Optional[bool] = False
) -> List[Artifact]:
    """If inputs is True, returning all input analytes of the process,
    otherwise returning all output analytes of the process"""

    if measurement:
        return get_qc_output_artifacts(lims=process.lims, process=process)
    elif input:
        return process.all_inputs(unique=True)
    else:
        return [a for a in process.all_outputs(unique=True) if a.type == "Analyte"]


def get_artifact_by_name(process: Process, name: str) -> Artifact:
    """Searches for output artifacts with name <file_name>
    Raises error if more than one artifact with same name!"""

    artifacts = list(filter(lambda a: a.name in [name], process.all_outputs()))

    if len(artifacts) > 1:
        raise FileError(f"more than one output artifact named {name}")

    return artifacts[0]


def filter_artifacts(artifacts: List[Artifact], udf: str, value) -> List[Artifact]:
    """Returning a list of only artifacts with udf==value"""

    return [a for a in artifacts if a.udf.get(udf) == value]


def get_latest_artifact(lims: Lims, sample_id: str, process_type: List[str]) -> Artifact:
    """Getting the most recently generated artifact by process_type and sample_id.

    Searching for all artifacts (Analytes) associated with <sample_id> that
    were produced by <process_type>.

    Returning the artifact with latest parent_process.date_run.
    If there are many such artifacts only one will be returned."""

    lims_artifacts = lims.get_artifacts(
        samplelimsid=sample_id,
        type="Analyte",
        process_type=process_type,
    )
    if not lims_artifacts:
        raise MissingArtifactError(
            f"Could not find a artifact with sample: {sample_id} generated by process: {' ,'.join(process_type)}"
        )

    artifacts = []
    for artifact in lims_artifacts:
        date = artifact.parent_process.date_run or datetime.today().strftime("%Y-%m-%d")
        artifacts.append((date, artifact.id, artifact))

    artifacts.sort()
    date, id, latest_art = artifacts[-1]

    return latest_art
