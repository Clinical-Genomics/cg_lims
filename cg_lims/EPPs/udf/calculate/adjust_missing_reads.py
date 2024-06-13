import logging
import sys

import click
from cg_lims.exceptions import LimsError, MissingCgFieldError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims.status_db_api import StatusDBAPI
from genologics.entities import Artifact
from requests.exceptions import ConnectionError

LOG = logging.getLogger(__name__)

def calculate_adjusted_reads(artifact: Artifact, factor: float) -> float:
    """A function to calculate the adjusted reads to sequence for each artifact with the desired apptag"""

    reads = sample.udf.get("Reads to sequence (M)")
    adjusted_reads = reads*factor
    return adjusted_reads

@click.command()
@options.apptag(help="String of UDF Sequencing Analysis, also known as apptag")
@options.factor(help="Factor to multiply Reads to sequence (M) with")
@options.threshold_reads(help="Threshold for determining which factor to adjust Reads to sequence (M) with for WGS topup samples")
@click.pass_context
def adjust_missing_reads(
    ctx: click.Context,
    apptag: str,
    factor: float,
    threshold_reads: float,
):
    """Script to calculate the adjusted Reads to sequence (M) with a specific factor for specific apptags, 
    specified in the command line"""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, measurement=True)
        for artifact in artifacts:
            if sample.udf.get("Sequencing Analysis") == apptag:
                adjusted_reads = calculate_adjusted_reads(artifact=artifact, factor=factor)
                artifact.udf["Reads to sequence (M)"] = adjusted_reads
                artifact.put()
        click.echo("Udfs have been updated on all samples.")
    except LimsError as e:
        sys.exit(e.message)
