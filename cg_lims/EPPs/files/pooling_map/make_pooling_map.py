import logging
import sys
from typing import List, Tuple
from datetime import date
import click
from genologics.entities import Artifact, Process
from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts
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

LOG = logging.getLogger(__name__)


def add_pool_info(pool_udfs: List[str], pool: Artifact) -> str:
    """Adding info about the pool"""

    html = []
    for udf in pool_udfs:
        value = pool.udf.get(udf)
        if value is not None:
            html.append(
                f'<tr><td class="group-field-label">{udf}: </td><td class="group-field-value">{value}</td></tr>'
            )
    return "".join(html)


def add_sample_info_headers(udfs_headers: List[str]) -> str:
    """Adding headers for more info about samples in the pool"""

    html = []
    for header in udfs_headers:
        html.append(f'<th style="width: 7%;" class="">{header}</th>')
    return "".join(html)


def add_sample_info(artifact: Artifact, udfs: List[str]) -> str:
    """Adding info about samples in the pool"""

    html = []
    for udf in udfs:
        value = artifact.udf.get(udf, "")
        html.append(f'<td class="" style="width: 7%;">{value}</td>')
    return "".join(html)


def make_html(
    pools: List[Artifact],
    process: Process,
    pool_udfs: List[str],
    sample_udfs: List[str],
) -> str:
    """Building the html for the pooling map"""

    html = []
    header_info = PlacementMapHeader(process_type=process.type.name, date=date.today().isoformat())
    html.append(PLACEMENT_MAP_HEADER.format(**header_info.dict()))

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
            pools_information=add_pool_info(pool_udfs, pool),
        )
        html.append(POOL_HEADER.format(**pool_info.dict()))
        extra_sample_columns: str = add_sample_info_headers(sample_udfs)
        html.append(SAMPLE_COLUMN_HEADERS.format(extra_sample_columns=extra_sample_columns))
        html.append("""</thead><tbody>""")

        for location, artifact in artifacts:
            sample = artifact.samples[0]
            sample_table_values = SampleTableSection(
                sample_id=sample.id,
                source_well=location,
                source_container=artifact.container.name,
                pool_name=pool.name,
                extra_sample_values=add_sample_info(artifact, sample_udfs),
            )
            html.append(SAMPLE_COLUMN_VALUES.format(**sample_table_values.dict()))
        html.append("""</tbody></table><br><br></html>""")

    html = "".join(html)
    return html


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.pool_udfs(help="Pool UDFs to show in the placement map.")
@options.sample_udfs(help="Sample UDFs to show in the placement map.")
@click.pass_context
def pool_map(ctx, file: str, sample_udfs: List[str], pool_udfs: List[str]):
    """Create a pool placement map."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    try:
        pools = get_artifacts(process=process, input=False)
        html = make_html(
            pools,
            process,
            pool_udfs,
            sample_udfs,
        )
        file = open(f"{file}.html", "w")
        file.write(html)
        file.close()
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
