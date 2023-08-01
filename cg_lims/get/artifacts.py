from typing import List, Optional, Literal

from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

from cg_lims.exceptions import FileError, MissingArtifactError
from datetime import datetime
import logging
from enum import Enum

LOG = logging.getLogger(__name__)


class OutputType(str, Enum):
    ANALYTE = "Analyte"
    RESULT_FILE = "ResultFile"


class OutputGenerationType(str, Enum):
    PER_INPUT = "PerInput"
    PER_REAGENT = "PerReagentLabel"
    PER_ALL_INPUTS = "PerAllInputs"


def get_sample_artifact(lims: Lims, sample: Sample) -> Artifact:
    """Returning the initial artifact related to a sample.
    Assuming first artifact is allways named sample.id + 'PA1."""
    sample_artifact_id = f"{sample.id}PA1"
    artifact = Artifact(lims, id=sample_artifact_id)
    try:
        artifact.get()
    except:
        message = f"no artifact with id {sample_artifact_id}"
        LOG.error(message)
        raise MissingArtifactError(message=message)
    return artifact


def get_output_artifacts(
    lims: Lims,
    process: Process,
    output_type: OutputType,
    output_generation_types: List[OutputGenerationType],
) -> List[Artifact]:
    """Get output 'artifacts' based on output_generation_type and output_type"""

    artifacts = [
        Artifact(lims, id=output["limsid"])
        for _, output in process.input_output_maps
        if output["output-generation-type"] in output_generation_types
        and output["output-type"] == output_type
    ]
    return list(frozenset(artifacts))


def get_artifacts(
    process: Process,
    input: Optional[bool] = False,
    measurement: Optional[bool] = False,
    reagent_label: Optional[bool] = False,
) -> List[Artifact]:
    """If inputs is True, returning all input analytes of the process,
    otherwise returning all output analytes of the process"""

    if input:
        return process.all_inputs(unique=True)
    elif measurement:
        return get_output_artifacts(
            lims=process.lims,
            process=process,
            output_type=OutputType.RESULT_FILE,
            output_generation_types=[OutputGenerationType.PER_INPUT],
        )
    elif reagent_label:
        return get_output_artifacts(
            lims=process.lims,
            process=process,
            output_type=OutputType.RESULT_FILE,
            output_generation_types=[OutputGenerationType.PER_REAGENT],
        )
    else:
        return get_output_artifacts(
            lims=process.lims,
            process=process,
            output_type=OutputType.ANALYTE,
            output_generation_types=[
                OutputGenerationType.PER_INPUT,
                OutputGenerationType.PER_ALL_INPUTS,
            ],
        )


def get_artifact_by_name(process: Process, name: str) -> Artifact:
    """Searches for output artifacts with name <file_name>
    Raises error if more than one artifact with same name!"""

    artifacts = list(filter(lambda a: a.name in [name], process.all_outputs()))

    if len(artifacts) > 1:
        message = f"more than one output artifact named {name}"
        LOG.error(message)
        raise FileError(message=message)

    return artifacts[0]


def filter_artifacts(artifacts: List[Artifact], udf: str, value) -> List[Artifact]:
    """Returning a list of only artifacts with udf==value"""

    if udf is None:
        return artifacts
    else:
        return [a for a in artifacts if a.udf.get(udf) == value]


def get_latest_artifact(lims_artifacts: List[Artifact]) -> Artifact:
    """Returning the latest generated artifact in the list of artifacts"""
    if not lims_artifacts:
        message = "Can not find latest artifact from a list of no artifacts"
        LOG.error(message)
        raise MissingArtifactError(message=message)

    artifacts = []
    for artifact in lims_artifacts:
        date = artifact.parent_process.date_run or datetime.today().strftime("%Y-%m-%d")
        artifacts.append((date, artifact.id, artifact))

    artifacts.sort()
    date, id, latest_art = artifacts[-1]
    return latest_art


def get_latest_analyte(
    lims: Lims,
    sample_id: str,
    process_types: Optional[List[str]],
    sample_artifact: bool = False,
) -> Artifact:
    """Getting the most recently generated analyte by process_types and sample_id.

    Searching for all Analytes associated with <sample_id> that were produced by <process_types>.

    Returning the analyte with latest parent_process.date_run.
    If there are many such artifacts only one will be returned."""

    if sample_artifact and not process_types:
        return get_sample_artifact(lims=lims, sample=Sample(lims, sample_id))

    lims_artifacts = lims.get_artifacts(
        samplelimsid=sample_id,
        type="Analyte",
        process_type=process_types,
    )

    if sample_artifact and not lims_artifacts:
        return get_sample_artifact(lims=lims, sample=Sample(lims, sample_id))

    if not lims_artifacts:
        message = f"Could not find a artifact with sample: {sample_id} generated by process: {' ,'.join(process_types)}"
        LOG.error(message)
        raise MissingArtifactError(message=message)

    return get_latest_artifact(lims_artifacts=lims_artifacts)

