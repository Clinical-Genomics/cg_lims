import datetime
import logging
from typing import Any, Dict, List, Tuple

import click
from cg_lims import options
from cg_lims.clients.cg.status_db_api import StatusDBAPI
from cg_lims.exceptions import LimsError
from genologics.entities import Artifact, Container, Process, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)

BCL_STEP = "Bcl Conversion & Demultiplexing (Nova Seq)"
DEFINE_RUN_STEPS = [
    "Define Run Format and Calculate Volumes (Nova Seq)",
    "Define Run Format and Calculate Volumes (NovaSeq X)",
]


def convert_to_datetime(date_string: str) -> datetime:
    """Return a datetime object from date string structured as YEAR-MONTH-DAY"""
    date: List[str] = date_string.split("-")
    return datetime.date(int(date[0]), int(date[1]), int(date[2]))


def is_within_timeframe(
    sequenced_at: datetime.date, from_date: datetime.date, to_date: datetime.date
) -> bool:
    """Check that the given sequenced at date is within the allowed timeframe."""
    return from_date < sequenced_at < to_date


def get_matching_samples(
    lims: Lims, from_date: datetime.date, to_date: datetime.date, apptags: List[str]
) -> List[Sample]:
    """Return all samples matching the given apptags and timeframe."""
    found_samples: List[Sample] = []
    for apptag in apptags:
        udf_dict: Dict[str, List[str]] = {"Sequencing Analysis": [apptag]}
        found_samples += lims.get_samples(udf=udf_dict)
    LOG.info(f"Total amount samples with matching apptags: {len(found_samples)}.")
    matching_samples: List[Sample] = []
    for sample in found_samples:
        sequenced_at: datetime.date = sample.udf.get("Sequencing Finished")
        if not sequenced_at or not is_within_timeframe(
            sequenced_at=sequenced_at, from_date=from_date, to_date=to_date
        ):
            continue
        LOG.info(f"Found matching sample {sample.id}.")
        matching_samples.append(sample)
    return matching_samples


def get_flow_cell_id(process: Process) -> str:
    """Return the flow cell ID of a given BCL Conv step."""
    prepare_seq_step: Process = process.parent_processes()[0]
    container: Container = prepare_seq_step.output_containers()[0]
    return container.name


def get_flow_cell_type(process: Process) -> str:
    """Return the flow cell type of a given BCL Conv step."""
    prepare_seq_step: Process = process.parent_processes()[0]
    return prepare_seq_step.udf.get("Run Mode")


def get_input_artifact(artifact: Artifact) -> Artifact:
    """Return the corresponding input artifact of a given output artifact."""
    process_inout_map: List[Tuple] = artifact.parent_process.input_output_maps
    for artifact_map in process_inout_map:
        if artifact_map[1]["limsid"] == artifact.id:
            return artifact_map[0]["uri"]


def get_loading_conc(artifact: Artifact) -> str:
    """Return the final loading concentration used for an artifact from a BCL conv step."""
    i = 0
    while artifact.parent_process.type.name not in DEFINE_RUN_STEPS:
        artifact = get_input_artifact(artifact=artifact)
        i += 1
        if i == 4:
            LOG.info(f"No Define Run Format step was found for artifact {artifact.id}. Skipping.")
            break
    return artifact.parent_process.udf.get("Final Loading Concentration (pM)")


def get_bcl_conv_artifacts(lims: Lims, sample: Sample) -> Dict[str, Any]:
    """Return a summary dictionary containing all BCL Conv steps, some key UDFs
    and also all output artifacts connected to the step for a given sample."""
    artifacts: List[Artifact] = lims.get_artifacts(
        type="ResultFile", process_type=BCL_STEP, samplelimsid=sample.id
    )
    artifact_dict = {}
    for artifact in artifacts:
        if not artifact.udf.get("# Reads"):
            continue
        parent_process: Process = artifact.parent_process
        if parent_process.id not in artifact_dict.keys():
            artifact_dict[parent_process.id] = {
                "date": parent_process.date_run,
                "flow cell ID": get_flow_cell_id(process=parent_process),
                "flow cell type": get_flow_cell_type(process=parent_process),
                "artifacts": [artifact],
            }
        else:
            artifact_dict[parent_process.id]["artifacts"].append(artifact)
    return artifact_dict


def get_target_amount(app_tag: str, status_db: StatusDBAPI) -> int:
    """Return the target amount of reads from clinical-api"""
    return status_db.get_application_tag(tag_name=app_tag, key="target_reads")


def get_times_sequenced(artifact_dict: Dict) -> int:
    """Return the number of times a sample has been sequenced given a previously generated summary dict."""
    return len(artifact_dict.keys())


def get_total_reads(artifacts: List[Artifact]) -> int:
    """Calculate and return the total amount of reads for a sample given a list of BCL Conv artifacts.
    Note: Only reads with Q30 values above 75% are accounted for."""
    total_reads = 0
    for artifact in artifacts:
        lane_reads = artifact.udf.get("# Reads")
        lane_q30 = artifact.udf.get("% Bases >=Q30")
        if not lane_reads or lane_q30 < 75:
            continue
        total_reads += lane_reads
    return total_reads


def calculate_missing_reads(total_reads: int, targeted_reads: int) -> int:
    """Calculate and return the missing reads of a sample given the current total and the targeted amount."""
    missing_reads = targeted_reads - total_reads
    if missing_reads < 0:
        return 0
    return missing_reads


def get_sample_row(sample: Sample, status_db: StatusDBAPI) -> str:
    """Return the .csv file row of a sample."""
    artifact_dict: Dict[str, Any] = get_bcl_conv_artifacts(lims=sample.lims, sample=sample)
    apptag: str = sample.udf.get("Sequencing Analysis")
    target_reads: int = get_target_amount(app_tag=apptag, status_db=status_db)
    times_sequenced: int = get_times_sequenced(artifact_dict=artifact_dict)
    row: str = (
        f"{sample.id},{sample.udf.get('Sequencing Analysis')},{target_reads},{times_sequenced}"
    )
    sorted_processes: List[str] = list(artifact_dict.keys())
    sorted_processes.sort()
    total_reads: int = 0
    for process in sorted_processes:
        loading_conc: str = get_loading_conc(artifact=artifact_dict[process]["artifacts"][0])
        reads_in_fc: int = get_total_reads(artifact_dict[process]["artifacts"])
        total_reads += reads_in_fc
        row += (
            f",{artifact_dict[process]['flow cell ID']},"
            f"{artifact_dict[process]['flow cell type']},"
            f"{loading_conc},{reads_in_fc},"
            f"{calculate_missing_reads(total_reads=total_reads, targeted_reads=target_reads)},"
            f"{round(100*total_reads/target_reads, 2)}"
        )
    return row


@click.command()
@options.file_placeholder(help="File name.")
@click.option(
    "--from-date",
    required=True,
    help="Earliest date to fetch data from.",
)
@click.option(
    "--to-date",
    required=True,
    help="Latest date to fetch data from.",
)
@options.apptag(help="Apptags to filter samples on.")
@click.pass_context
def create_topup_summary(
    ctx: click.Context, file: str, from_date: str, to_date: str, apptag: List[str]
) -> None:

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims: Lims = ctx.obj["lims"]
    status_db: StatusDBAPI = ctx.obj["status_db"]

    try:
        header: str = (
            "sample,apptag,target reads,# times sequenced,"
            "flow cell 1,flow cell 1 type,loading conc (pM) 1,# reads run 1,# reads missing run 1,% targeted run 1,"
            "flow cell 2,flow cell 2 type,loading conc (pM) 2,# reads run 2,# missing reads run 2,% targeted run 2,"
            "flow cell 3,flow cell 3 type,loading conc (pM) 3,# reads run 3,# reads missing run 3,% targeted run 3,"
            "flow cell 4,flow cell 4 type,loading conc (pM) 4,# reads run 4,# reads missing run 4,% targeted run 4"
        )
        from_date: datetime = convert_to_datetime(date_string=from_date)
        to_date: datetime = convert_to_datetime(date_string=to_date)
        samples: List[Sample] = get_matching_samples(
            lims=lims, from_date=from_date, to_date=to_date, apptags=apptag
        )
        print(f"Found {len(samples)} matching samples!")
        LOG.info(f"Found {len(samples)} matching samples!")
        with open(file, "w") as file:
            file.write(header + "\n")
            for sample in samples:
                file_row: str = get_sample_row(sample=sample, status_db=status_db)
                file.write(file_row + "\n")
        message: str = f"Top-up summary created!\nNumber of samples in file: {len(samples)}"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        click.echo(e.message)
