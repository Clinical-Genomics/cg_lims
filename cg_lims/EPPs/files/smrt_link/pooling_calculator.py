import logging
import re
import sys
from typing import Dict, List, Optional, Tuple

import click
from cg_lims import options
from cg_lims.EPPs.files.smrt_link.models import PoolingCalculator
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifact_lane, get_artifacts
from genologics.entities import Artifact, Process, ReagentType, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


@click.command()
@options.file_placeholders(help="File placeholder names.")
@click.pass_context
def create_smrtlink_pooling_calculation(ctx, files: Tuple[str]):
    """Create pooling calculation .csv files for SMRT Link import."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        files_list = list(files)
        pools: List[Artifact] = get_artifacts(process=process)
        if len(pools) > len(files_list):
            raise InvalidValueError(
                f"Maximum number of pools for SMRT Link import is {len(files_list)}!"
            )
        for pool in pools:
            pool_calculation: PoolingCalculator = PoolingCalculator(pool_artifact=pool)
            pool_csv = pool_calculation.build_csv()
            with open(f"{files_list.pop()}_{pool.name}.csv", "w") as file:
                file.write(pool_csv)
        click.echo("The pooling calculation CSVs were successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
