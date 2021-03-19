import logging
import sys
from typing import List
import click
from datetime import date
from genologics.entities import Artifact, Process
from genologics.lims import Lims
from cg_lims import options
from cg_lims.exceptions import LimsError
from .models import PlacementMapHeader, WellInfo, PlateInfo
from .hmtl_templates import (
    PLACEMENT_MAP_HEADER,
    PLATE_HEADER_SECTION,
    TABLE_HEADERS,
    TABLE_ROWS,
    VISUAL_PLACEMENT_MAP_HEADER,
    VISUAL_PLACEMENT_MAP_WEL,
)

LOG = logging.getLogger(__name__)


def get_placement_map_data(
    lims: Lims, process: Process, udfs: List[str], original_well: str
) -> dict:
    """collecting the data for the placement map."""

    placement_map = {}
    for inp, outp in process.input_output_maps:
        if outp.get("output-generation-type") == "PerAllInputs":
            continue
        in_art = Artifact(lims, id=inp["limsid"])
        out_art = Artifact(lims, id=outp["limsid"])
        dest_cont = out_art.location[0]
        dest_well = out_art.location[1]
        if dest_cont:
            if not dest_cont in placement_map:
                placement_map[dest_cont] = {}
            placement_map[dest_cont][dest_well] = make_source_dest_info(
                in_art, out_art, original_well, udfs
            )
    return placement_map


def make_source_dest_info(
    source_artifact: Artifact, dest_artifact: Artifact, original_well: str, udfs: List[str]
) -> WellInfo:
    """Collecting info about a well."""

    sample = source_artifact.samples[0]
    if original_well:
        container_type = "Original Container"
        container = sample.udf.get("Original Container", "")
        well_type = "Original Well"
        well = sample.udf.get("Original Well", "")
    else:
        container_type = "Source Container"
        container = source_artifact.location[0].id
        well_type = "Source Well"
        well = source_artifact.location[1]
    return WellInfo(
        project_name=sample.project.name,
        sample_name=sample.name,
        sample_id=sample.id,
        container_type=container_type,
        container=container,
        well_type=well_type,
        well=well,
        exta_udf_info=more_sample_info(source_artifact, udfs),
        dest_well=dest_artifact.location[1],
    )


def more_sample_info(artifact: Artifact, udfs: List[str]) -> str:
    """Adding info about sample in the well"""

    html = []
    for udf in udfs:
        value = artifact.udf.get(udf)
        if value is not None:
            if isinstance(value, float):
                value = round(value, 2)
            html.append(f"{udf} : {value}")
    return "".join(html)


def make_html(placement_map: dict, process: Process):
    """"""

    html = []
    html.append("<html>")
    header_info = PlacementMapHeader(process_type=process.type.name, date=date.today().isoformat())
    html.append(PLACEMENT_MAP_HEADER.format(**header_info.dict()))
    for container, container_info in placement_map.items():
        plate_info = PlateInfo(
            container_name=container.name,
            container_type=container.type.name,
            container_id=container.id,
        )
        html.append(""""<table class="group-contents"><br><br><thead>""")
        html.append(PLATE_HEADER_SECTION.format(**plate_info.dict()))
        html.append(TABLE_HEADERS)
        html.append("</thead>")
        html.append("<tbody>")
        for dest_well, well_data in container_info.items():
            html.append(TABLE_ROWS.format(**well_data.dict()))
        html.append("</tbody></table><br><br>")

        ## VISUAL Platemap

        html.append(VISUAL_PLACEMENT_MAP_HEADER)
        html.append("<tbody>")

        coulmns = range(1, 14)
        rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        for rowname in rows:
            html.append(
                f"""
                <tr style="height: 12%;">
                <td class="bold-column row-name">{rowname}</td>"""
            )
            for column in coulmns:
                well_location = f"{rowname}:{column}"
                if well_location in container_info:
                    # This only happens if there is an artifact in the well
                    # This assumes that all artifacts have the required UDFs
                    well_info = container_info[well_location]
                    html.append(VISUAL_PLACEMENT_MAP_WEL.format(**well_info.dict()))
                else:
                    # For wells that are empty:
                    html.append('<td class="well" style="">&nbsp;</td>')
            html.append("</tr>")
        html.append("</body></table>")
    html.append("</html>")
    html = "".join(html)
    return html


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.sample_udfs(help="Sample UDFs to show in the placement map.")
@options.original_well()
@click.pass_context
def placement_map(ctx, file: str, sample_udfs: List[str], original_well):
    """Create a 96 well placement map."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        placement_map_data = get_placement_map_data(lims, process, sample_udfs, original_well)
        html = make_html(placement_map_data, process)
        file = open(f"{file}.html", "w")
        file.write(html)
        file.close()
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
