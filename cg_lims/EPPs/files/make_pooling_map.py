import logging
import sys
from typing import List
from datetime import date
import click
from genologics.entities import Artifact, Process
from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts
from .hmtl_templates import POOL_TEMPLATE

LOG = logging.getLogger(__name__)


def add_pool_info(pool_udfs: List[str], pool: Artifact):
    html = []
    for udf in pool_udfs:
        value = pool.udf.get(udf)
        if value is not None:
            html.append(
                f'<tr><td class="group-field-label">{udf}: </td><td class="group-field-value"></td></tr>{value}'
            )
    return "".join(html)


def add_sample_info_headers(udfs: List[str]):
    html = []
    for udf in udfs:
        html.append(f'<th style="width: 7%;" class="">{udf}</th>')
    return "".join(html)


def add_sample_info(sample: Artifact, sample_udfs: List[str]):
    html = []
    for udf in sample_udfs:
        value = sample.udf.get(udf, "")
        if value is not None:
            html.append(f'<td class="" style="width: 7%;">{value}</td>')
    return "".join(html)


def make_html(
    pools: List[Artifact],
    process: Process,
    pool_udfs: List[str],
    sample_udfs: List[str],
):
    ### HEADER ###
    html = []
    html.append(
        f"""
        <html>
        <head>
        <style>table, th, td {{border: 1px solid black; border-collapse: collapse;}}</style>
        <meta content="text/html; charset=UTF-8" http-equiv="Content-Type">
        <link href="../css/g/queue-print.css" rel="stylesheet" type="text/css" media="screen,print">
        <title>{process.type.name}</title>
        </head>
        <body>
        <div id="header">
        <h1 class="title">{process.type.name}</h1>
        </div>
        Created: {date.today().isoformat()}"""
    )

    ### POOLS ###
    for pool in pools:
        artifacts = [(a.location[1], a) for a in pool.input_artifact_list()]
        # sorting on columns
        artifacts.sort(key=lambda tup: tup[0][1])
        pool_info = {
            "nr_samples": len(artifacts),
            "pool_name": pool.name,
            "pool_id": pool.id,
            "pools_information": add_pool_info(pool_udfs, pool),
        }

        # Information about the pool
        html.append(POOL_TEMPLATE.format(**pool_info))
        # html.append(POOL_TEMPLATE.format(**pool_info.dict())

        # Information about samples the pool
        ## Columns Header
        html.append(
            f"""<tr>
                <th style="width: 7%;" class="">Sample Lims ID</th>
                <th style="width: 7%;" class="">Source Well</th>
                <th style="width: 7%;" class="">Source Container</th>
                <th style="width: 7%;" class="">Pool Name</th>
                {add_sample_info_headers(sample_udfs)}
                </tr>"""
        )
        html.append(
            """</thead>
            <tbody>"""
        )

        ## artifact list
        for location, art in artifacts:
            sample = art.samples[0]

            html.append(
                f"""
            <tr>
            <td style="width: 7%;">{sample.id}</td>
            <td class="" style="width: 7%;">{location}</td>
            <td class="" style="width: 7%;">{art.container.name}</td>
            <td class="" style="width: 7%;">{pool.name}</td>
            {add_sample_info(sample, sample_udfs)}
            </tr>"""
            )
        html.append(
            """
            </tbody>
            </table>
            <br><br>
            </html>"""
        )
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
    except LimsError as e:
        sys.exit(e.message)
