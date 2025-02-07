import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


@click.command()
@options.concentration_udf()
@options.amount_udf_option()
@options.volume_udf_option()
@options.total_volume_process_udf()
@options.subtract_volume()
@options.preset_volume()
@options.measurement()
@options.input()
@click.pass_context
def calculate_amount_ng(
    ctx: click.Context,
    amount_udf: str,
    volume_udf: str,
    total_volume_pudf: str,
    concentration_udf: str,
    subtract_volume: str,
    preset_volume: float,
    measurement: bool = False,
    input: bool = False,
):
    """Calculates and auto-fills the quantities of DNA in sample from concentration and volume
    measurements. The volume can be subtracted by an optional specification in the cli. This is
    because the lab uses some microliters of the sample in the qc measurements. A pre-set
    volume can be set in the cli as well."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(
            process=process, measurement=measurement, input=input
        )
        missing_udfs_count: int = 0
        artifacts_with_missing_udf: List = []
        for artifact in artifacts:
            if preset_volume:
                vol: float = float(preset_volume)
            elif total_volume_pudf:
                vol: float = process.udf.get(total_volume_pudf)
            elif volume_udf:
                vol: float = artifact.udf.get(volume_udf)
            conc: float = artifact.udf.get(concentration_udf)
            if None in [conc, vol]:
                missing_udfs_count += 1
                artifacts_with_missing_udf.append(artifact.id)
                continue
            artifact.udf[amount_udf] = conc * (vol - int(subtract_volume))
            artifact.put()
        if missing_udfs_count:
            raise MissingUDFsError(
                f"Udf missing for {missing_udfs_count} artifact(s): "
                f"{','.join(artifacts_with_missing_udf)}. "
            )
        message: str = "Amounts have been calculated for all artifacts."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
