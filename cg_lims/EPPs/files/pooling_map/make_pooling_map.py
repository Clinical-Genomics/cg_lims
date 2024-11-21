import logging
import sys
from datetime import date
from typing import List, Optional, Tuple

import click
from cg_lims import options
from cg_lims.EPPs.files.pooling_map.hmtl_templates import (
    PLACEMENT_MAP_HEADER,
    POOL_HEADER,
    SAMPLE_COLUMN_HEADERS,
    SAMPLE_COLUMN_VALUES,
)
from cg_lims.EPPs.files.pooling_map.models import (
    PlacementMapHeader,
    PoolSection,
    SampleTableSection,
)
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process
from matplotlib import colors

COLORS = list(colors.XKCD_COLORS.values())
LOG = logging.getLogger(__name__)


def add_pool_info(
    pool_udfs: List[str],
    pool: Artifact,
    round_decimals: Optional[int],
) -> str:
    """Adding info about the pool"""

    html = []
    for udf in pool_udfs:
        value = pool.udf.get(udf)
        if value is not None:
            if round_decimals and type(value) is float:
                value = round(value, round_decimals)
            html.append(
                f'<tr><td class="group-field-label">{udf}: </td><td class="group-field-value">{value}</td></tr>'
            )
    return "".join(html)


def add_sample_info_headers(udfs_headers: List[str]) -> str:
    """Adding headers for more info about samples in the pool"""

    html = [f'<th style="width: 7%;" class="">{header}</th>' for header in udfs_headers]

    return "".join(html)


def add_sample_info(artifact: Artifact, udfs: List[str], round_decimals: Optional[int]) -> str:
    """Adding info about samples in the pool"""

    html = []
    for udf in udfs:
        value = artifact.udf.get(udf)
        if round_decimals and type(value) is float:
            value = round(value, round_decimals)
        html.append(f'<td class="" style="width: 7%;">{value}</td>')
    return "".join(html)


def make_html(
    pools: List[Artifact],
    process: Process,
    pool_udfs: List[str],
    sample_udfs: List[str],
    round_decimals: Optional[int],
) -> str:
    """Building the html for the pooling map"""

    html = []
    header_info = PlacementMapHeader(process_type=process.type.name, date=date.today().isoformat())
    html.append(PLACEMENT_MAP_HEADER.format(**header_info.dict()))

    source_containers = {}
    for pool in pools:
        artifacts: List[Tuple[str, Artifact]] = [
            (artifact.location[1], artifact) for artifact in pool.input_artifact_list()
        ]
        # sorting on columns
        artifacts.sort(key=lambda tup: tup[0][1])

        pool_info = PoolSection(
            nr_samples=len(artifacts),
            pool_name=pool.name,
            pool_id=pool.id,
            pools_information=add_pool_info(
                pool_udfs=pool_udfs, pool=pool, round_decimals=round_decimals
            ),
        )
        html.append(POOL_HEADER.format(**pool_info.dict()))
        extra_sample_columns: str = add_sample_info_headers(sample_udfs)
        html.append(SAMPLE_COLUMN_HEADERS.format(extra_sample_columns=extra_sample_columns))
        html.append("""</thead><tbody>""")
        for location, artifact in artifacts:
            sample = artifact.samples[0]
            sample_warning_color = "#F08080" if artifact.udf.get("Warning") else "#FFFFFF"
            if artifact.container.name not in source_containers.keys():
                source_container_color = COLORS[0]
                COLORS.pop(0)
                source_containers[artifact.container.name] = source_container_color
            sample_table_values = SampleTableSection(
                sample_id=sample.id,
                sample_warning_color=sample_warning_color,
                source_well=location,
                source_container=artifact.container.name,
                source_container_color=source_containers[artifact.container.name],
                pool_name=pool.name,
                extra_sample_values=add_sample_info(
                    artifact=artifact, udfs=sample_udfs, round_decimals=round_decimals
                ),
            )
            html.append(SAMPLE_COLUMN_VALUES.format(**sample_table_values.dict()))
        html.append("""</tbody></table><br><br></html>""")

    html = "".join(html)
    return html


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.pool_udfs(help="Pool UDFs to show in the placement map.")
@options.sample_udfs(help="Sample UDFs to show in the placement map.")
@options.round_decimals()
@click.pass_context
def pool_map(
    ctx, file: str, sample_udfs: List[str], pool_udfs: List[str], round_decimals: str = None
):
    """Create a pool placement map."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    try:
        if round_decimals:
            round_decimals = int(round_decimals)
        pools = get_artifacts(process=process, input=False)
        pools.sort(key=lambda x: x.id)
        html = make_html(
            pools=pools,
            process=process,
            pool_udfs=pool_udfs,
            sample_udfs=sample_udfs,
            round_decimals=round_decimals,
        )
        with open(f"{file}.html", "w") as file:
            file.write(html)
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
