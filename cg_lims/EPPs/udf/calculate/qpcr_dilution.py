import logging
import sys
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional

import click
import numpy as np
import pandas as pd
from cg_lims import options
from cg_lims.EPPs.udf.calculate.constants import WELL_TRANSFORMER
from cg_lims.exceptions import FailingQCError, LimsError, MissingFileError
from cg_lims.get.artifacts import get_artifact_by_name, get_artifacts
from cg_lims.get.files import get_file_path
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def parse_quantification_summary(summary_file: str) -> Dict:
    """Parse Quantification Summary excel file and return python dict with
    original wells as the keys and WellValues objects as the values."""
    df = pd.read_excel(summary_file)
    quantification_data = {}
    for index, row in df.iterrows():
        well = row["Well"]
        cq = round(row["Cq"], 3)
        sq = row["SQ"]
        if not (np.isnan(cq) or np.isnan(sq)):
            orig_well = WELL_TRANSFORMER[well]
            if orig_well not in quantification_data.keys():
                quantification_data[orig_well] = WellValues(well=orig_well)
            quantification_data[orig_well].add_values(sq_value=sq, cq_value=cq)
    return quantification_data


def calculate_molar_concentration(sq_values: List[float], size_bp: int):
    """Calculate and return the molar concentration given a list of SQ values and a fragment size."""
    original_conc = mean(sq_values) * 10**4
    return original_conc * (452 / size_bp)


def get_index_of_biggest_outlier(values: List[float]) -> int:
    """Return the index of the largest outlier in the given list of values."""
    mean_value = mean(values)
    dev_from_mean = [abs(value - mean_value) for value in values]
    max_dev = max(dev_from_mean)
    return dev_from_mean.index(max_dev)


def get_max_difference(values: List[float]) -> float:
    """Return the difference between the largest and smallest values in a given list of values."""
    return max(values) - min(values)


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
        self.artifact = artifact

    def _trim_outliers(self) -> str:
        """Remove the largest outlier of the current Cq and SQ values."""
        outlier_index = get_index_of_biggest_outlier(values=self.cq)
        removed_cq_value = self.cq.pop(outlier_index)
        removed_sq_value = self.sq.pop(outlier_index)
        return f"Removed outlier Cq value {removed_cq_value} and SQ value {removed_sq_value} from {self.artifact.samples[0].id}."

    def get_concentration(self, cq_threshold: float, size_bp: int) -> float:
        """Return the concentration (M) of the well object, given a Cq difference threshold and fragment size."""
        cq_set_difference = get_max_difference(self.cq)
        if cq_set_difference > cq_threshold:
            message = (
                f" Cq value difference is too high between the replicates of sample {self.artifact.samples[0].id}.\n"
                f"Difference: {cq_set_difference}\n"
                f"Cq values: {self.cq}\n"
                f"SQ values: {self.sq}\n"
            )
            trim_log = self._trim_outliers()
            message = message + trim_log
            LOG.info(message)
        return calculate_molar_concentration(sq_values=self.sq, size_bp=size_bp)

    def set_artifact_udfs(
        self, concentration_threshold: float, replicate_threshold: float, size_bp: int
    ) -> None:
        """Calculate and set all UDFs and QC flags of the connected artifact."""
        molar_concentration = self.get_concentration(
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


@click.command()
@options.file_placeholder(help="qPCR result file placeholder name.")
@options.local_file()
@options.replicate_threshold()
@options.concentration_threshold()
@options.size_bp()
@click.pass_context
def qpcr_dilution(
    ctx,
    file: str,
    local_file: str,
    replicate_threshold: str,
    concentration_threshold: str,
    size_bp: str,
) -> None:
    """Script for calculating qPCR dilutions. Requires an input qPCR result file and produces an output log file."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    if local_file:
        file_path = local_file
    else:
        file_art = get_artifact_by_name(process=process, name=file)
        file_path = get_file_path(file_art)

    if not Path(file_path).is_file():
        raise MissingFileError(f"No such file: {file_path}")

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, measurement=True)
        quantification_data = parse_quantification_summary(summary_file=file_path)
        failed_samples = 0
        for artifact in artifacts:
            well_results: WellValues = quantification_data[artifact.location[1]]
            well_results.connect_artifact(artifact=artifact)
            well_results.set_artifact_udfs(
                concentration_threshold=float(concentration_threshold),
                replicate_threshold=float(replicate_threshold),
                size_bp=int(size_bp),
            )
            if well_results.artifact.qc_flag == "FAILED":
                failed_samples += 1

        if failed_samples:
            error_message = (
                f"{failed_samples} sample(s) failed the QC! See the logs for further information."
            )
            raise FailingQCError(error_message)

        message = "Concentrations have been calculated and set for all samples!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
