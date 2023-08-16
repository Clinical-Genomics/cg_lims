import re
import logging
import sys
import click

from typing import List, Optional, Dict
from genologics.lims import Lims
from genologics.entities import Artifact, Process, ReagentType
from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError
from cg_lims.get.artifacts import get_artifact_lane, get_artifacts
from cg_lims.EPPs.files.sample_sheet.models import (
    IndexSetup,
    IndexType,
    SampleSheetHeader,
    IlluminaIndex,
    NovaSeqXRun,
    LaneSample,
)


LOG = logging.getLogger(__name__)


def get_non_pooled_artifacts(artifact: Artifact) -> List[Artifact]:
    """Return the parent artifact of the sample. Should hold the reagent_label"""
    artifacts: List[Artifact] = []

    if len(artifact.samples) == 1:
        artifacts.append(artifact)
        return artifacts

    for artifact in artifact.input_artifact_list():
        artifacts.extend(get_non_pooled_artifacts(artifact))
    return artifacts


def get_reagent_label(artifact: Artifact) -> Optional[str]:
    """Return the first and only reagent label from an artifact"""
    labels: List[str] = artifact.reagent_labels
    if len(labels) > 1:
        LOG.error(
            f"Got an unexpected amount of reagent labels ({len(labels)}), for artifact {artifact.id}."
        )
        raise ValueError(f"Expecting at most one reagent label. Got {len(labels)}.")
    return labels[0] if labels else None


def get_reagent_index(lims: Lims, label: str) -> str:
    """Return the index sequence from a given reagent label"""

    reagent_types: List[ReagentType] = lims.get_reagent_types(name=label)

    if len(reagent_types) > 1:
        LOG.error(
            f"Got an unexpected amount of reagent types ({len(reagent_types)}), for label {label}."
        )
        raise ValueError(f"Expecting at most one reagent type. Got {len(reagent_types)}.")

    try:
        reagent_type = reagent_types.pop()
    except IndexError:
        return ""
    sequence: str = reagent_type.sequence

    match = re.match(r"^.+ \((.+)\)$", label)
    if match and match.group(1) != sequence:
        LOG.error(
            f"Given reagent label name ({label}) doesn't match its index sequence ({sequence})."
        )
        raise ValueError(
            f"Given reagent label name ({label}) doesn't match its index sequence ({sequence})."
        )

    return sequence


def get_sample_indexes(artifact: Artifact) -> List[IlluminaIndex]:
    """Return the indexes that the sample has been prepped with."""
    reagent: str = get_reagent_label(artifact=artifact)
    index_sequences: List[str] = get_reagent_index(lims=artifact.lims, label=reagent).split("-")
    indexes: List[IlluminaIndex] = [
        IlluminaIndex(sequence=index_sequences[0], type=IndexType.INDEX_1)
    ]
    if index_sequences[1]:
        indexes.append(IlluminaIndex(sequence=index_sequences[1], type=IndexType.INDEX_2))
    return indexes


def sort_lanes(lane_artifacts: Dict[int, Artifact]) -> Dict[int, Artifact]:
    """Return a sorted version of the same dictionary by lane number."""
    return dict(sorted(lane_artifacts.items()))


def get_lane_artifacts(process: Process) -> Dict[int, Artifact]:
    """Return a sorted dictionary consisting of all pools in a given step and their lane position."""
    artifacts: List[Artifact] = get_artifacts(process=process)
    lane_artifacts: Dict = {}
    for artifact in artifacts:
        lane = get_artifact_lane(artifact=artifact)
        lane_artifacts[lane] = artifact
    return sort_lanes(lane_artifacts=lane_artifacts)


def create_bcl_settings_section(run_settings: NovaSeqXRun) -> str:
    """Return the BCLConvert_Settings section of the sample sheet."""
    return (
        f"{SampleSheetHeader.BCL_SETTINGS_SECTION}\n"
        f"SoftwareVersion,{run_settings.bclconvert_software_version}\n"
        f"FastqCompressionFormat,{run_settings.fastq_compression_format}\n\n"
    )


def get_index_list(artifacts: List[Artifact]) -> List[IlluminaIndex]:
    """Return a list containing all indexes present in a list of given artifacts."""
    index_list: List[IlluminaIndex] = []
    for artifact in artifacts:
        indexes: List[IlluminaIndex] = get_sample_indexes(artifact=artifact)
        index_list.extend(indexes)
    return index_list


def string_hamming_distance(index_1: str, index_2: str) -> Optional[int]:
    """Return the hamming distance of two strings."""
    if len(index_1) != len(index_2):
        return None
    return sum(n1 != n2 for n1, n2 in zip(index_1, index_2))


def calculate_index_hamming_distance(
    index_1: IlluminaIndex, index_2: IlluminaIndex
) -> Optional[int]:
    """Calculate and return the hamming distance of two indexes."""
    if index_1.type != index_2.type:
        return None
    elif len(index_1.sequence) == len(index_2.sequence):
        return string_hamming_distance(index_1=index_1.sequence, index_2=index_2.sequence)
    elif len(index_1.sequence) < len(index_2.sequence):
        if index_1.type == IndexType.INDEX_1:
            return string_hamming_distance(
                index_1=index_1.sequence, index_2=index_2.sequence[: len(index_1.sequence)]
            )
        elif index_1.type == IndexType.INDEX_2:
            return string_hamming_distance(
                index_1=index_1.sequence, index_2=index_2.sequence[-len(index_1.sequence) :]
            )
    else:
        if index_1.type == IndexType.INDEX_1:
            return string_hamming_distance(
                index_1=index_1.sequence[: len(index_2.sequence)], index_2=index_2.sequence
            )
        elif index_1.type == IndexType.INDEX_2:
            return string_hamming_distance(
                index_1=index_1.sequence[-len(index_2.sequence) :], index_2=index_2.sequence
            )
    message: str = f"Non-supported index type identified for indexes {index_1.sequence} and {index_2.sequence}: '{index_1.type}'."
    LOG.error(message)
    raise InvalidValueError(message)


def get_barcode_mismatches(index: IlluminaIndex, all_indexes: List[IlluminaIndex]) -> int:
    """Return the highest number of barcode mismatches allowed for an index."""
    if len(all_indexes) > len(set(all_indexes)):
        message: str = f"Duplicate indexes have been identified! Aborting sample sheet generation."
        LOG.error(message)
        raise InvalidValueError(message)
    for comparison_index in all_indexes:
        hamming_distance: int = calculate_index_hamming_distance(
            index_1=index, index_2=comparison_index
        )
        if comparison_index.sequence == index.sequence or hamming_distance is None:
            continue
        elif hamming_distance < 3:
            LOG.info(
                f"Low hamming distance ({hamming_distance}) found between indexes {index.sequence} and {comparison_index.sequence}. "
                f"Setting barcode mismatches to 0."
            )
            return 0
    return 1


def get_lane_sample_object(
    run_settings: NovaSeqXRun, lane: int, artifact: Artifact, all_indexes: List[IlluminaIndex]
) -> LaneSample:
    """Return a LaneSample object representing the data of a lane-sample row in the BCLConvert_Data section."""
    indexes: List[IlluminaIndex] = get_sample_indexes(artifact=artifact)
    if len(indexes) == IndexSetup.DUAL_INDEX:
        barcode_mismatch_index_1: int = get_barcode_mismatches(
            index=indexes[0], all_indexes=all_indexes
        )
        barcode_mismatch_index_2: int = get_barcode_mismatches(
            index=indexes[1], all_indexes=all_indexes
        )
        return LaneSample(
            run_settings=run_settings,
            lane=lane,
            sample_id=artifact.samples[0].id,
            index_1=indexes[0].sequence,
            index_2=indexes[1].sequence,
            barcode_mismatch_index_1=barcode_mismatch_index_1,
            barcode_mismatch_index_2=barcode_mismatch_index_2,
        )
    elif len(indexes) == IndexSetup.SINGLE_INDEX:
        barcode_mismatch_index_1: int = get_barcode_mismatches(
            index=indexes[0], all_indexes=all_indexes
        )
        return LaneSample(
            run_settings=run_settings,
            lane=lane,
            sample_id=artifact.samples[0],
            index_1=indexes[0].sequence,
            index_2=None,
            barcode_mismatch_index_1=barcode_mismatch_index_1,
            barcode_mismatch_index_2=None,
        )
    message: str = f"Expecting 1 or 2 total indexes. Got ({len(indexes)})."
    LOG.error(message)
    raise ValueError(message)


def create_bcl_data_section(run_settings: NovaSeqXRun) -> str:
    """Return the BCLConvert_Data section of the sample sheet."""
    section: str = f"{SampleSheetHeader.BCL_DATA_SECTION}\n"
    section = section + run_settings.get_bcl_data_header_row()
    lane_artifacts: Dict[int, Artifact] = get_lane_artifacts(process=run_settings.process)
    for lane in lane_artifacts:
        unpooled_artifacts: List[Artifact] = get_non_pooled_artifacts(artifact=lane_artifacts[lane])
        pool_indexes: List[IlluminaIndex] = get_index_list(artifacts=unpooled_artifacts)
        for artifact in unpooled_artifacts:
            lane_sample = get_lane_sample_object(
                run_settings=run_settings,
                lane=lane,
                artifact=artifact,
                all_indexes=pool_indexes,
            )
            section = section + lane_sample.get_bclconversion_data_row()
    return section


def create_sample_sheet_from_process(process: Process) -> str:
    """Return the sample sheet content from a given sequencing run set-up process."""
    run_settings: NovaSeqXRun = NovaSeqXRun(process=process)
    return (
        run_settings.create_head_section()
        + run_settings.create_reads_section()
        + create_bcl_settings_section(run_settings=run_settings)
        + create_bcl_data_section(run_settings=run_settings)
    )


@click.command()
@options.file_placeholder(help="File placeholder name.")
@click.pass_context
def create_sample_sheet(ctx, file: str):
    """Create a sample sheet .csv file from a sequencing set-up step."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        sample_sheet_content: str = create_sample_sheet_from_process(process=process)
        run_name: str = process.udf.get("BaseSpace Run Name")
        with open(f"{file}_samplesheet_{run_name}.csv", "w") as file:
            file.write(sample_sheet_content)
        click.echo("The sample sheet was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
