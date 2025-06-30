import logging
import sys
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Tuple

import click
import numpy as np
import pandas as pd
from cg_lims import options
from cg_lims.EPPs.udf.calculate.constants import WELL_TRANSFORMER
from cg_lims.exceptions import (
    FailingQCError,
    FileError,
    InvalidContainerError,
    LimsError,
    MissingFileError,
    MissingValueError,
)
from cg_lims.get.artifacts import get_artifact_by_name, get_artifacts
from cg_lims.get.files import get_file_path
from cg_lims.get.samples import get_one_sample_from_artifact
from genologics.entities import Artifact, Container, Process

LOG = logging.getLogger(__name__)


class WellValues:
    def __init__(self, well):
        self.well: str = well
        self.sq: List[float] = []
        self.cq: List[float] = []
        self.viable_indexes: List[List[int]] = []
        self.artifact: Optional[Artifact] = None

    def add_values(self, sq_value: float, cq_value: float) -> None:
        """Add Cq and SQ values to the well object."""
        self.sq.append(sq_value)
        self.cq.append(cq_value)

    def connect_artifact(self, artifact: Artifact) -> None:
        """Connect an artifact to the well object."""
        self.artifact: Artifact = artifact

    def _trim_outliers(self) -> str:
        """Remove the largest outlier of the current Cq and SQ values."""
        outlier_index: int = get_index_of_biggest_outlier(values=self.cq)
        removed_cq_value: float = self.cq.pop(outlier_index)
        removed_sq_value: float = self.sq.pop(outlier_index)
        return f"Removed outlier Cq value {removed_cq_value} and SQ value {removed_sq_value} from {self.artifact.samples[0].id}."

    def get_concentration(self, cq_threshold: float, size_bp: int) -> float:
        """Return the concentration (M) of the well object, given a Cq difference threshold and fragment size."""
        cq_set_difference: float = get_max_difference(self.cq)
        if cq_set_difference > cq_threshold:
            message: str = (
                f" Cq value difference is too high between the replicates of sample {self.artifact.samples[0].id}.\n"
                f"Difference: {cq_set_difference}\n"
                f"Cq values: {self.cq}\n"
                f"SQ values: {self.sq}\n"
            )
            trim_log: str = self._trim_outliers()
            message = message + trim_log
            LOG.info(message)
        return calculate_molar_concentration(sq_values=self.sq, size_bp=size_bp)

    def set_artifact_udfs(
        self, concentration_threshold: float, replicate_threshold: float, size_bp: int
    ) -> None:
        """Calculate and set all UDFs and QC flags of the connected artifact."""
        molar_concentration: float = self.get_concentration(
            cq_threshold=float(replicate_threshold), size_bp=int(size_bp)
        )
        self.artifact.qc_flag = "PASSED"
        self.artifact.udf["Size (bp)"] = int(size_bp)
        self.artifact.udf["Concentration"] = molar_concentration
        self.artifact.udf["Concentration (nM)"] = molar_concentration * 10**9
        if self.artifact.udf["Concentration (nM)"] < concentration_threshold:
            self.artifact.qc_flag = "FAILED"
            LOG.info(
                f" Concentration of {self.artifact.samples[0].id} is {molar_concentration * 10**9} nM."
                f" Setting QC flag to failed as this is below the threshold of {concentration_threshold} nM."
            )
        self.artifact.put()


def parse_quantification_summary(summary_file: Path) -> Dict[str, WellValues]:
    """Parse Quantification Summary excel file and return python dict with
    original wells as the keys and WellValues objects as the values."""
    df: pd.DataFrame = pd.read_excel(summary_file)
    quantification_data: Dict = {}
    for index, row in df.iterrows():
        well: str = row["Well"]
        cq: float = round(row["Cq"], 3)
        sq: float = row["SQ"]
        if not (np.isnan(cq) or np.isnan(sq)):
            orig_well: str = WELL_TRANSFORMER[well]
            if orig_well not in quantification_data.keys():
                quantification_data[orig_well] = WellValues(well=orig_well)
            quantification_data[orig_well].add_values(sq_value=sq, cq_value=cq)
    return quantification_data


def calculate_molar_concentration(sq_values: List[float], size_bp: int):
    """Calculate and return the molar concentration given a list of SQ values and a fragment size."""
    return (mean(sq_values) * 10**4) * (452 / size_bp)


def get_index_of_biggest_outlier(values: List[float]) -> int:
    """Return the index of the largest outlier in the given list of values."""
    mean_value: float = mean(values)
    dev_from_mean: List[float] = [abs(value - mean_value) for value in values]
    max_dev: float = max(dev_from_mean)
    return dev_from_mean.index(max_dev)


def get_max_difference(values: List[float]) -> float:
    """Return the difference between the largest and smallest values in a given list of values."""
    return max(values) - min(values)


def set_missing_artifact_values(artifact: Artifact, size_bp: int) -> None:
    """Set UDF values for samples that are missing values from the qPCR files."""
    artifact.qc_flag = "FAILED"
    artifact.udf["Size (bp)"] = size_bp
    artifact.udf["Concentration"] = 0
    artifact.udf["Concentration (nM)"] = 0
    artifact.put()


def get_container_name(process: Process) -> str:
    """Return the name of the container available in the step. Will fail if more than one is found."""
    containers: List[Container] = process.output_containers()
    if len(containers) > 1:
        raise InvalidContainerError(
            f"Warning: Can't fetch container name. Only one is allowed in the step."
        )
    return containers[0].name


@click.command()
@options.file_placeholder(help="qPCR result file placeholder name.")
@options.local_file()
@options.replicate_threshold()
@options.concentration_threshold()
@options.size_bp()
@options.ignore_fail(help="Use this flag if you want to override the file name check.")
@click.pass_context
def qpcr_concentration(
    ctx,
    file: str,
    local_file: str,
    replicate_threshold: str,
    concentration_threshold: str,
    size_bp: str,
    ignore_fail: bool = False,
) -> None:
    """Script for calculating qPCR dilutions. Requires an input qPCR result file and produces an output log file."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    if local_file:
        file_path: Path = Path(local_file)
    else:
        file_art: Artifact = get_artifact_by_name(process=process, name=file)
        file_path: Path = Path(get_file_path(file_art))

    if not file_path.is_file():
        raise MissingFileError(f"No such file: {file_path}")

    container_name: str = get_container_name(process=process)

    if not ignore_fail and container_name not in file_path.name:
        raise FileError(
            f"The file name ('{file_path.name}') does not match the given container ({container_name})! "
            f"Please check that the correct file has been used."
        )

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, measurement=True)
        quantification_data: Dict[str, WellValues] = parse_quantification_summary(
            summary_file=file_path
        )
        failed_samples: int = 0
        missing_samples: List[Tuple[str, str]] = []
        for artifact in artifacts:
            artifact_well: str = artifact.location[1]
            if artifact_well not in quantification_data.keys():
                sample_id: str = get_one_sample_from_artifact(artifact=artifact).id
                missing_samples.append((sample_id, artifact_well))
                set_missing_artifact_values(artifact=artifact, size_bp=int(size_bp))
                LOG.warning(
                    f" Sample {sample_id} in well {artifact_well} is missing qPCR values. Setting QC to fail."
                )
                continue
            well_results: WellValues = quantification_data[artifact.location[1]]
            well_results.connect_artifact(artifact=artifact)
            well_results.set_artifact_udfs(
                concentration_threshold=float(concentration_threshold),
                replicate_threshold=float(replicate_threshold),
                size_bp=int(size_bp),
            )
            if well_results.artifact.qc_flag == "FAILED":
                failed_samples += 1

        if missing_samples:
            raise MissingValueError(
                f"No values found for the following samples in the result file! "
                f"Please check if the samples {missing_samples} have been placed correctly."
            )

        if failed_samples:
            error_message: str = (
                f" {failed_samples} sample(s) failed the QC! See the logs for further information."
            )
            raise FailingQCError(error_message)

        message: str = " Concentrations have been calculated and set for all samples!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
