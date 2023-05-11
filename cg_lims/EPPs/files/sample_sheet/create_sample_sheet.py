import re
import logging
import sys
import click

from typing import List, Optional, Dict
from genologics.lims import Artifact, Process, Lims
from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError, MissingValueError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.EPPs.files.sample_sheet.models import SampleSheetHeader, NovaSeqXRun, LaneSample


LOG = logging.getLogger(__name__)


def get_artifact_lane(artifact: Artifact) -> int:
    ""Return the lane where an artifact is placed"""
    return int(artifact.location[1].split(":")[0])


def get_non_pooled_artifacts(artifact: Artifact) -> List[Artifact]:
    """Return the parent artifact of the sample. Should hold the reagent_label"""
    artifacts: List[Artifact] = []

    if len(artifact.samples) == 1:
        artifacts.append(artifact)
        return artifacts

    for artifact_input in artifact.input_artifact_list():
        artifacts.extend(get_non_pooled_artifacts(artifact_input))
    return artifacts


def get_reagent_label(artifact) -> Optional[str]:
    """Return the first and only reagent label from an artifact"""
    labels: List[str] = artifact.reagent_labels
    if len(labels) > 1:
        raise ValueError("Expecting at most one reagent label. Got ({}).".format(len(labels)))
    return labels[0] if labels else None


def get_index(lims: Lims, label: str) -> str:
    """Parse out the sequence from a reagent label"""

    reagent_types = lims.get_reagent_types(name=label)

    if len(reagent_types) > 1:
        raise ValueError("Expecting at most one reagent type. Got ({}).".format(len(reagent_types)))

    try:
        reagent_type = reagent_types.pop()
    except IndexError:
        return ""
    sequence = reagent_type.sequence

    match = re.match(r"^.+ \((.+)\)$", label)
    if match:
        assert match.group(1) == sequence

    return sequence


def get_sample_indexes(artifact: Artifact) -> List[str]:
    reagent = get_reagent_label(artifact=artifact)
    index_string = get_index(lims=artifact.lims, label=reagent)
    return index_string.split("-")


def sort_lanes(lane_artifacts: Dict[int, Artifact]) -> Dict[int, Artifact]:
    return dict(sorted(lane_artifacts.items()))


def get_lane_artifacts(process: Process) -> Dict[int, Artifact]:
    artifacts = get_artifacts(process=process)
    lane_artifacts = {}
    for artifact in artifacts:
        lane = get_artifact_lane(artifact=artifact)
        lane_artifacts[lane] = artifact
    return sort_lanes(lane_artifacts=lane_artifacts)


def create_bcl_settings_section(run_settings: NovaSeqXRun) -> str:
    return (
        f"{SampleSheetHeader.BCL_SETTINGS_SECTION}\n"
        f"SoftwareVersion,{run_settings.bclconvert_software_version}\n"
        f"FastqCompressionFormat,{run_settings.fastq_compression_format}\n\n"
    )


def get_lane_sample_object(run_settings: NovaSeqXRun, lane: int, artifact: Artifact) -> LaneSample:
    indexes = get_sample_indexes(artifact=artifact)
    if len(indexes) == 2:
        return LaneSample(
            run_settings=run_settings,
            lane=lane,
            sample_id=artifact.samples[0].id,
            index1=indexes[0],
            index2=indexes[1],
        )
    elif len(indexes) == 1:
        return LaneSample(
            run_settings=run_settings,
            lane=lane,
            sample_id=artifact.samples[0],
            index1=indexes[0],
            index2=None,
        )
    raise ValueError(f"Expecting 1 or 2 total indexes. Got ({len(indexes)}).")


def create_bcl_data_section(run_settings: NovaSeqXRun) -> str:
    section : str = f"{SampleSheetHeader.BCL_DATA_SECTION}\n"
    section = section + run_settings.get_bcl_data_header()
    lane_artifacts = get_lane_artifacts(run_settings.process)
    for lane in lane_artifacts:
        unpooled_artifacts = get_non_pooled_artifacts(lane_artifacts[lane])
        for artifact in unpooled_artifacts:
            lane_sample = get_lane_sample_object(
                run_settings=run_settings, lane=lane, artifact=artifact
            )
            section = section + lane_sample.get_bclconversion_data()
    return section


def create_sample_sheet_from_process(process: Process) -> str:
    run_settings: NovaSeqXRun = NovaSeqXRun(process=process)
    return (
        run_settings.create_file_header_section()
        + run_settings.create_reads_section()
        + create_bcl_settings_section(run_settings=run_settings)
        + create_bcl_data_section(run_settings=run_settings)
    )


@click.command()
@options.file_placeholder(help="File placeholder name.")
@click.pass_context
def create_sample_sheet(ctx, file: str):
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        sample_sheet = create_sample_sheet_from_process(process=process)
        run_name: str = process.udf.get("Experiment Name")
        with open(f"{file}_samplesheet_{run_name}.csv", "w") as file:
            file.write(sample_sheet)
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
