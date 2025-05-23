import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional, Set, Tuple

from cg_lims.exceptions import FileError, InvalidValueError, MissingArtifactError
from cg_lims.get.fields import get_alternative_artifact_well, get_artifact_well
from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


class OutputType(str, Enum):
    ANALYTE = "Analyte"
    RESULT_FILE = "ResultFile"


class OutputGenerationType(str, Enum):
    PER_INPUT = "PerInput"
    PER_REAGENT = "PerReagentLabel"
    PER_ALL_INPUTS = "PerAllInputs"


ARTIFACT_KEY = "uri"


def get_artifact_lane(artifact: Artifact) -> int:
    """Return the lane where an artifact is placed"""
    return int(artifact.location[1].split(":")[0])


def get_lane_sample_artifacts(process: Process) -> List[Tuple[int, Artifact]]:
    """Return a list of tuples (lane number, Artifact) detailing the artifacts on each lane in a BCL Convert step."""
    lane_sample_artifacts: Set = set()

    for input_map, output_map in process.input_output_maps:
        try:
            if is_output_type_per_reagent(output_map):
                output_artifact: Artifact = get_artifact_from_map(output_map)
                input_artifact: Artifact = get_artifact_from_map(input_map)
                lane: int = get_artifact_lane(input_artifact)

                lane_sample_artifacts.add((lane, output_artifact))
        except KeyError:
            continue

    return list(lane_sample_artifacts)


def get_smrt_cell_sample_artifacts(
    process: Process, smrt_cell_udf: str
) -> List[Tuple[str, Artifact]]:
    """
    Return a list of tuples (cell ID, Artifact) detailing the artifacts
    on each SMRT Cell in a Demultiplex Revio Run step.
    """
    smrt_cell_sample_artifacts: Set = set()

    for input_map, output_map in process.input_output_maps:
        try:
            if is_output_type_per_reagent(output_map):
                output_artifact: Artifact = get_artifact_from_map(output_map)
                input_artifact: Artifact = get_artifact_from_map(input_map)
                smrt_cell_id: str = input_artifact.udf.get(smrt_cell_udf)

                smrt_cell_sample_artifacts.add((smrt_cell_id, output_artifact))
        except KeyError:
            continue

    return list(smrt_cell_sample_artifacts)


def is_output_type_per_reagent(output_map: Dict) -> bool:
    """Check if the output type is per reagent for a given output map."""
    return output_map["output-generation-type"] == OutputGenerationType.PER_REAGENT


def get_artifact_from_map(map: Dict) -> Artifact:
    """Return the artifact for a given input or output map."""
    return map[ARTIFACT_KEY]


def get_sample_artifact(lims: Lims, sample: Sample) -> Artifact:
    """
    Return the initial artifact related to a sample.
    Assuming first artifact is always named sample.id + 'PA1.
    """
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
    """
    If inputs is True, returning all input analytes of the process,
    otherwise returning all output analytes of the process
    """

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
    """
    Searches for output artifacts with name <file_name>
    Raises error if more than one artifact with same name!
    """

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
    """
    Getting the most recently generated analyte by process_types and sample_id.

    Searching for all Analytes associated with <sample_id> that were produced by <process_types>.

    Returning the analyte with latest parent_process.date_run.
    If there are many such artifacts only one will be returned.
    """

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


def get_latest_result_files(
    lims: Lims,
    sample_id: str,
    process_types: Optional[List[str]],
    output_generation_type: Literal["PerInput", "PerReagentLabel"],
) -> List[Artifact]:
    """
    This function will make a lot of queries if the nr of artifacts in the step are many and the artifacts are pools.
    (At least 3+2n+nk queries to teh database, where n is the number of input artifacts and k is the number of samples
    per artifact if artifact is pool.)

    Only use this function if you have to.
    """

    all_result_files = lims.get_artifacts(
        samplelimsid=sample_id,
        type="ResultFile",
        process_type=process_types,
    )
    sample = Sample(lims=lims, id=sample_id)
    latest = get_latest_artifact(lims_artifacts=all_result_files)
    latest_process: Process = latest.parent_process

    specific_result_files = []
    for input, output in latest_process.input_output_maps:
        if output["output-generation-type"] != output_generation_type:
            continue
        artifact = Artifact(lims, id=output["limsid"])
        if sample not in artifact.samples:
            continue

        specific_result_files.append(artifact)

    if not specific_result_files:
        message = f"Could not find a artifact with sample: {sample_id} generated by process: {' ,'.join(process_types)}"
        LOG.error(message)
        raise MissingArtifactError(message=message)

    return specific_result_files


def get_non_pooled_artifacts(artifact: Artifact) -> List[Artifact]:
    """Return the parent artifact of the sample. Should hold the reagent_label"""
    artifacts: List[Artifact] = []

    if len(artifact.samples) == 1:
        artifacts.append(artifact)
        return artifacts

    for artifact in artifact.input_artifact_list():
        artifacts.extend(get_non_pooled_artifacts(artifact))
    return artifacts


def create_well_dict(
    process: Process,
    input_flag: bool = False,
    native_well_format: bool = False,
    quantit_well_format: bool = False,
) -> Dict[str, Artifact]:
    """Creates a well dict based on the input_output_map
    keys: well of input artifact
    values: input/output artifact depending on the input flag
    """

    well_dict: Dict[str, Artifact] = {}
    lims: Lims = process.lims
    for input, output in process.input_output_maps:
        if output.get("output-generation-type") == "PerAllInputs":
            continue
        input_artifact = Artifact(lims, id=input["limsid"])
        output_artifact = Artifact(lims, id=output["limsid"])
        source_artifact: Artifact = input_artifact if input_flag else output_artifact
        if native_well_format:
            well: str = source_artifact.location[1]
        elif quantit_well_format:
            well: str = get_alternative_artifact_well(artifact=source_artifact)
        else:
            well: str = get_artifact_well(artifact=source_artifact)
        if well in well_dict.keys():
            raise InvalidValueError(
                f"Can't create dictionary! Well {well} is already used by another artifact."
            )
        well_dict[well] = output_artifact
    return well_dict
