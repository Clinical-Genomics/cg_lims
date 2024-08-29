import logging
import sys

import click
from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact

LOG = logging.getLogger(__name__)


def calculate_adjusted_reads(artifact: Artifact, factor: str) -> float:
    """A function to calculate the adjusted reads to sequence for each artifact with the desired apptag"""

    reads = artifact.udf.get("Reads to sequence (M)")
    return round(float(reads) * float(factor), 1)


def adjust_wgs_topups(
    artifact: Artifact, factor_wgs_lower: str, factor_wgs_higher: str, threshold_reads: str
) -> None:
    """A function that calculates adjusted reads to sequence for WGS topups, where the 'topup' factor is determined
    by a threshold for the reads to sequence. This is specified in the cli"""

    valid_value = validate_udf_values(artifact=artifact)

    if valid_value:
        reads = float(artifact.udf.get("Reads to sequence (M)"))
        if reads < float(threshold_reads):
            adjusted_reads = round(float(reads) * float(factor_wgs_lower), 1)
        else:
            adjusted_reads = round(float(reads) * float(factor_wgs_higher), 1)
        artifact.udf["Reads to sequence (M)"] = str(adjusted_reads)
        artifact.put()


def reset_microbial_reads(artifact: Artifact, reset_microbial_reads: str) -> None:
    """A function that resets the reads to sequence for microbial samples, and the threshold_reads specifies what they are
    supposed to be reset to"""

    valid_value = validate_udf_values(artifact=artifact)

    if valid_value:
        artifact.udf["Reads to sequence (M)"] = reset_microbial_reads
        artifact.put()


def is_topup(artifact: Artifact) -> bool:
    """A function that determines whether an artifact has already been sequenced before or not, and therefore is a topup
    sample/artifact"""

    output = False
    if artifact.samples[0].udf.get("Total Reads (M)"):
        output = True
    return output


def is_adjusted(artifact: Artifact) -> bool:
    """A function that checks if the process UDF Adjusted Reads to Sequence is set/true. This will
    be updated after the EPP to adjust the reads to sequence has run one time"""

    process = artifact.parent_process
    output = False
    if process.udf.get("Adjusted Reads to Sequence"):
        output = True
    return output


def validate_udf_values(artifact: Artifact) -> bool:
    """A function checking whether Reads to Sequence (M) has a negative/no value.
    Then the function returns the output as 'False' and logs all those sample IDs in the EPP log"""

    output = True
    if (
        not artifact.udf.get("Reads to sequence (M)")
        or float(artifact.udf.get("Reads to sequence (M)")) < 0
    ):
        output = False
        LOG.info(
            f"Sample {artifact.samples[0].id} has no or a negative value for Reads to sequence (M). Skipping."
        )
    return output


def adjust_reads(artifact: Artifact, apptags: tuple, factor: str) -> None:
    """Only artifacts that have passed the validation of acceptable Reads to Sequence (M) values will be adjusted"""

    valid_value = validate_udf_values(artifact=artifact)

    if valid_value:
        adjusted_reads = calculate_adjusted_reads(artifact=artifact, factor=factor)
        artifact.udf["Reads to sequence (M)"] = str(adjusted_reads)
        artifact.put()


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

    process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process)
        for artifact in artifacts:
            if not is_adjusted(artifact=artifact):
                for app in apptag_wgs:
                    if app in artifact.samples[0].udf.get("Sequencing Analysis") and is_topup(
                        artifact=artifact
                    ):
                        adjust_wgs_topups(
                            artifact=artifact,
                            factor_wgs_lower=factor_wgs_lower,
                            factor_wgs_higher=factor_wgs_higher,
                            threshold_reads=threshold_reads,
                        )
                for app in apptag_wgs_tumor:
                    if app in artifact.samples[0].udf.get("Sequencing Analysis"):
                        if is_topup(artifact=artifact):
                            adjust_wgs_topups(
                                artifact=artifact,
                                factor_wgs_lower=factor_wgs_lower,
                                factor_wgs_higher=factor_wgs_higher,
                                threshold_reads=threshold_reads,
                            )
                        else:
                            adjust_reads(
                                artifact=artifact, apptags=apptag_wgs_tumor, factor=factor_wgs_tumor
                            )
                for app in apptag_tga:
                    if app in artifact.samples[0].udf.get("Sequencing Analysis"):
                        if is_topup(artifact=artifact):
                            adjust_reads(
                                artifact=artifact, apptags=apptag_tga, factor=factor_tga_topups
                            )
                        else:
                            adjust_reads(artifact=artifact, apptags=apptag_tga, factor=factor_tga)
                for app in apptag_micro:
                    if app in artifact.samples[0].udf.get("Sequencing Analysis"):
                        if is_topup(artifact=artifact):
                            reset_microbial_reads(
                                artifact=artifact, reset_microbial_reads=reset_micro_reads
                            )
                        else:
                            adjust_reads(
                                artifact=artifact, apptags=apptag_micro, factor=factor_micro
                            )
                for app in apptag_virus:
                    if app in artifact.samples[0].udf.get("Sequencing Analysis") and is_topup(
                        artifact=artifact
                    ):
                        reset_microbial_reads(
                            artifact=artifact, reset_microbial_reads=reset_virus_reads
                        )
                for app in apptag_rml:
                    if app in artifact.samples[0].udf.get("Sequencing Analysis"):
                        if is_topup(artifact=artifact):
                            adjust_reads(
                                artifact=artifact, apptags=apptag_rml, factor=factor_rml_topups
                            )
                        else:
                            adjust_reads(artifact=artifact, apptags=apptag_rml, factor=factor_rml)
                for app in apptag_rna:
                    if app in artifact.samples[0].udf.get("Sequencing Analysis"):
                        if is_topup(artifact=artifact):
                            adjust_reads(
                                artifact=artifact, apptags=apptag_rna, factor=factor_rna_topups
                            )
                        else:
                            adjust_reads(artifact=artifact, apptags=apptag_rna, factor=factor_rna)
            if is_adjusted(artifact=artifact):
                LOG.info("Samples have already been adjusted.")
        click.echo("Udfs have been updated on all samples.")
        process.udf["Adjusted Reads to Sequence"] = True
        process.put()
    except LimsError as e:
        sys.exit(e.message)
