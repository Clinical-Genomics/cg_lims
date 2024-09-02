import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def calculate_adjusted_reads(artifact: Artifact, factor: str) -> float:
    """A function to calculate the adjusted reads to sequence for each artifact with the desired apptag"""

    reads: str = artifact.udf.get("Reads to sequence (M)")
    adjusted_reads: float = round(float(reads) * float(factor), 1)
    LOG.info(f"Reads adjusted for sample {artifact.samples[0].id}: {reads}M -> {adjusted_reads}M")
    return adjusted_reads


def adjust_wgs_topups(
    artifact: Artifact, factor_wgs_lower: str, factor_wgs_higher: str, threshold_reads: str
) -> None:
    """A function that calculates adjusted reads to sequence for WGS topups, where the 'topup' factor is determined
    by a threshold for the reads to sequence. This is specified in the cli"""

    valid_value: bool = validate_udf_values(artifact=artifact)

    if valid_value:
        reads: float = float(artifact.udf.get("Reads to sequence (M)"))
        if reads < float(threshold_reads):
            adjusted_reads: float = calculate_adjusted_reads(
                artifact=artifact, factor=factor_wgs_lower
            )
        else:
            adjusted_reads: float = calculate_adjusted_reads(
                artifact=artifact, factor=factor_wgs_higher
            )
        artifact.udf["Reads to sequence (M)"] = str(adjusted_reads)
        artifact.put()


def reset_microbial_reads(artifact: Artifact, reset_reads: str) -> None:
    """A function that resets the reads to sequence for microbial samples, and the threshold_reads specifies what they are
    supposed to be reset to"""

    valid_value: bool = validate_udf_values(artifact=artifact)

    if valid_value:
        LOG.info(
            f"Reads reset for sample {artifact.samples[0].id}: {artifact.udf.get('Reads to sequence (M)')}M -> {reset_reads}M"
        )
        artifact.udf["Reads to sequence (M)"] = reset_reads
        artifact.put()


def is_topup(artifact: Artifact) -> bool:
    """A function that determines whether an artifact has already been sequenced before or not, and therefore is a topup
    sample/artifact"""

    output: bool = False
    if (
        artifact.samples[0].udf.get("Total Reads (M)")
        and artifact.samples[0].udf.get("Total Reads (M)") != 0
    ):
        output = True
    return output


def is_adjusted(process: Process) -> bool:
    """A function that checks if the process UDF Adjusted Reads to Sequence is set/true. This will
    be updated after the EPP to adjust the reads to sequence has run one time"""

    output: bool = False
    if process.udf.get("Adjusted Reads to Sequence"):
        output = True
    return output


def validate_udf_values(artifact: Artifact) -> bool:
    """A function checking whether Reads to Sequence (M) has a negative/no value.
    Then the function returns the output as 'False' and logs all those sample IDs in the EPP log"""

    output: bool = True
    if (
        not artifact.udf.get("Reads to sequence (M)")
        or float(artifact.udf.get("Reads to sequence (M)")) < 0
    ):
        output = False
        LOG.info(
            f"Sample {artifact.samples[0].id} has no or a negative value for Reads to sequence (M). Skipping."
        )
    return output


def adjust_reads(artifact: Artifact, factor: str) -> None:
    """Only artifacts that have passed the validation of acceptable Reads to Sequence (M) values will be adjusted"""

    valid_value: bool = validate_udf_values(artifact=artifact)

    if valid_value:
        adjusted_reads: float = calculate_adjusted_reads(artifact=artifact, factor=factor)
        artifact.udf["Reads to sequence (M)"] = str(adjusted_reads)
        artifact.put()


def adjust_wgs_artifact_reads(
    artifact: Artifact,
    reads_threshold: str,
    lower_topup_factor: str,
    higher_topup_factor: str,
    factor: Optional[str] = None,
) -> None:
    """A function for adjusting the reads of a WGS sample. The logic goes:
    - Top-ups with read amounts above the 'reads_threshold' value will be adjusted according to 'higher_topup_factor'
    - Top-ups with read amount below the 'reads_threshold' value will be adjusted according to 'lower_topup_factor'
    - Non top-ups will be adjusted according to the optional 'factor' value
    - Non top-up samples are untouched if no 'factor' value is given"""

    if is_topup(artifact=artifact):
        adjust_wgs_topups(
            artifact=artifact,
            factor_wgs_lower=lower_topup_factor,
            factor_wgs_higher=higher_topup_factor,
            threshold_reads=reads_threshold,
        )
    elif factor:
        adjust_reads(artifact=artifact, factor=factor)


def adjust_artifact_reads(
    artifact: Artifact,
    topup_factor: str,
    factor: Optional[str] = None,
) -> None:
    """A function for adjusting the reads of a sample. The logic goes:
    - Top-ups will be adjusted according to the 'topup_factor' value
    - Non top-ups will be adjusted according to the optional 'factor' value
    - Non top-up samples are untouched if no 'factor' value is given"""

    if is_topup(artifact=artifact):
        adjust_reads(artifact=artifact, factor=topup_factor)
    elif factor:
        adjust_reads(artifact=artifact, factor=factor)


def adjust_micro_artifact_reads(
    artifact: Artifact,
    reset_amount: str,
    factor: Optional[str] = None,
) -> None:
    """A function for adjusting the reads of a microbial sample. The logic goes:
    - The reads of a top-up sample gets reset according to the value of 'reset_amount'
    - Non top-up samples will be adjusted according to the optional 'factor' value
    - Non top-up samples are untouched if no 'factor' value is given"""

    if is_topup(artifact=artifact):
        reset_microbial_reads(artifact=artifact, reset_reads=reset_amount)
    elif factor:
        adjust_reads(artifact=artifact, factor=factor)


@click.command()
@options.apptag_wgs(help="String of UDF Sequencing Analysis, also known as apptag, for WGS samples")
@options.apptag_wgs_tumor(
    help="String of UDF Sequencing Analysis, also known as apptag, for WGS tumor samples"
)
@options.apptag_tga(help="String of UDF Sequencing Analysis, also known as apptag, for TGA samples")
@options.apptag_micro(
    help="String of UDF Sequencing Analysis, also known as apptag, for micro samples"
)
@options.apptag_rml(help="String of UDF Sequencing Analysis, also known as apptag, for RML samples")
@options.apptag_virus(
    help="String of UDF Sequencing Analysis, also known as apptag, for virus samples"
)
@options.apptag_rna(help="String of UDF Sequencing Analysis, also known as apptag, for RNA samples")
@options.factor_wgs_tumor(
    help="Factor to multiply Reads to sequence (M) with for WGS tumor samples"
)
@options.factor_tga(help="Factor to multiply Reads to sequence (M) with for TGA samples")
@options.factor_micro(help="Factor to multiply Reads to sequence (M) with for micro samples")
@options.factor_rml(help="Factor to multiply Reads to sequence (M) with for RML samples")
@options.factor_rna(help="Factor to multiply Reads to sequence (M) with for RNA samples")
@options.factor_rna_topups(
    help="Factor to multiply Reads to sequence (M) with for RNA topup samples"
)
@options.factor_rml_topups(
    help="Factor to multiply Reads to sequence (M) with for RML topup samples"
)
@options.factor_tga_topups(
    help="Factor to multiply Reads to sequence (M) with for TGA topup samples"
)
@options.factor_wgs_lower(
    help="Lower factor to multiply Reads to sequence (M) with for WGS samples"
)
@options.factor_wgs_higher(
    help="Higher factor to multiply Reads to sequence (M) with for WGS samples"
)
@options.threshold_reads(help="Threshold for Reads to sequence (M) during adjustment")
@options.reset_micro_reads(help="A value to re-set Reads to sequence (M) for microbial samples")
@options.reset_virus_reads(help="A value to re-set Reads to sequence (M) for virus samples")
@click.pass_context
def adjust_missing_reads(
    ctx: click.Context,
    apptag_wgs: tuple,
    apptag_wgs_tumor: tuple,
    apptag_tga: tuple,
    apptag_micro: tuple,
    apptag_rml: tuple,
    apptag_virus: tuple,
    apptag_rna: tuple,
    factor_wgs_tumor: str,
    factor_tga: str,
    factor_micro: str,
    factor_rml: str,
    factor_rna: str,
    factor_rna_topups: str,
    factor_rml_topups: str,
    factor_tga_topups: str,
    factor_wgs_lower: str,
    factor_wgs_higher: str,
    threshold_reads: str,
    reset_micro_reads: str,
    reset_virus_reads: str,
):
    """Script to calculate the adjusted Reads to sequence (M) with a specific factor for specific apptags,
    specified in the command line"""

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process)
        if is_adjusted(process=process):
            warning_message = "Samples have already been adjusted!"
            LOG.warning(warning_message)
            raise InvalidValueError(warning_message)
        for artifact in artifacts:
            sample_apptag: str = artifact.samples[0].udf.get("Sequencing Analysis")
            for app in apptag_wgs:
                if app in sample_apptag:
                    adjust_wgs_artifact_reads(
                        artifact=artifact,
                        lower_topup_factor=factor_wgs_lower,
                        higher_topup_factor=factor_wgs_higher,
                        reads_threshold=threshold_reads,
                    )
            for app in apptag_wgs_tumor:
                if app in sample_apptag:
                    adjust_wgs_artifact_reads(
                        artifact=artifact,
                        lower_topup_factor=factor_wgs_lower,
                        higher_topup_factor=factor_wgs_higher,
                        reads_threshold=threshold_reads,
                        factor=factor_wgs_tumor,
                    )
            for app in apptag_tga:
                if app in sample_apptag:
                    adjust_artifact_reads(
                        artifact=artifact, topup_factor=factor_tga_topups, factor=factor_tga
                    )
            for app in apptag_rml:
                if app in sample_apptag:
                    adjust_artifact_reads(
                        artifact=artifact, topup_factor=factor_rml_topups, factor=factor_rml
                    )
            for app in apptag_rna:
                if app in sample_apptag:
                    adjust_artifact_reads(
                        artifact=artifact, topup_factor=factor_rna_topups, factor=factor_rna
                    )
            for app in apptag_micro:
                if app in sample_apptag:
                    adjust_micro_artifact_reads(
                        artifact=artifact, reset_amount=reset_micro_reads, factor=factor_micro
                    )
            for app in apptag_virus:
                if app in sample_apptag:
                    adjust_micro_artifact_reads(artifact=artifact, reset_amount=reset_virus_reads)
        process.udf["Adjusted Reads to Sequence"] = True
        process.put()
        success_message = "Udfs have been updated on all samples."
        LOG.info(success_message)
        click.echo(success_message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
