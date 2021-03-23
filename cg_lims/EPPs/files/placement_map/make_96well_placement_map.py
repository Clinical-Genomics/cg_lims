import logging
import sys
from typing import List, Dict
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
    VISUAL_PLACEMENT_MAP_WELL,
)

LOG = logging.getLogger(__name__)


def get_placement_map_data(
    lims: Lims, process: Process, udfs: List[str], original_well: str
) -> dict:
    """collecting the data for the placement map."""

    placement_map = {}
    for input, output in process.input_output_maps:
        if output.get("output-generation-type") == "PerAllInputs":
            continue
        input_artifact = Artifact(lims, id=input["limsid"])
        output_artifact = Artifact(lims, id=output["limsid"])
        destination_container = output_artifact.location[0]
        if destination_container:
            if destination_container not in placement_map:
                placement_map[destination_container] = {}
            destination_well = output_artifact.location[1]
            placement_map[destination_container][destination_well] = make_source_dest_info(
                input_artifact, output_artifact, original_well, udfs
            )
    return placement_map


def make_source_dest_info(
    source_artifact: Artifact, dest_artifact: Artifact, original_well: str, udfs: List[str]
) -> WellInfo:
    """Collecting info about a well."""

    sample = source_artifact.samples[0]
    if len(source_artifact.samples) > 1:
        sample_name = source_artifact.name
        sample_id = source_artifact.id
        sample_type = "Pool"
    else:
        sample_name = sample.name
        sample_id = sample.id
        sample_type = "Sample"

    if original_well:
        container_source = "Original Container"
        container_name = sample.udf.get("Original Container", "")
        well_source = "Original Well"
        well = sample.udf.get("Original Well", "")
    else:
        container_source = "Source Container"
        container_name = source_artifact.location[0].name
        well_source = "Source Well"
        well = source_artifact.location[1]
    return WellInfo(
        project_name=sample.project.name,
        sample_name=sample_name,
        sample_id=sample_id,
        sample_type=sample_type,
        container_source=container_source,
        container_name=container_name,
        well_source=well_source,
        well=well,
        exta_udf_info=more_sample_info(source_artifact, udfs),
        dest_well=dest_artifact.location[1],
    )


def more_sample_info(artifact: Artifact, udfs: List[str]) -> str:
    """Adding more udf info about sample in the well."""

    html = []
    for udf in udfs:
        value = artifact.udf.get(udf)
        if value is not None:
            if isinstance(value, float):
                value = round(value, 2)
            html.append(f"{udf} : {value}")
    return "".join(html)


def add_wells(container_info: Dict[str, WellInfo]):
    """Building the plate wells for the visual placement map."""

    html = []
    coulmns = range(1, 14)
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for rowname in rows:
        html.append(f"""<tr style="height: 12%;"><td class="bold-column row-name">{rowname}</td>""")
        for column in coulmns:
            well_location = f"{rowname}:{column}"
            if well_location in container_info:
                # If there is an artifact in the well:
                well_info = container_info[well_location]
                html.append(VISUAL_PLACEMENT_MAP_WELL.format(**well_info.dict()))
            else:
                # For wells that are empty:
                html.append('<td class="well" style="">&nbsp;</td>')
        html.append("</tr>")
    return "".join(html)


def make_html(placement_map: dict, process: Process, original_well: str) -> str:
    """Creating the html."""

    html = ["<html>"]
    header_info = PlacementMapHeader(process_type=process.type.name, date=date.today().isoformat())
    html.append(PLACEMENT_MAP_HEADER.format(**header_info.dict()))
    container_source = "Original" if original_well else "Source"
    for container, container_info in placement_map.items():
        plate_info = PlateInfo(
            container_name=container.name,
            container_type=container.type.name,
            container_id=container.id,
        )
        html.append("""<table class="group-contents"><br><br><thead>""")
        html.append(PLATE_HEADER_SECTION.format(**plate_info.dict()))
        html.append(TABLE_HEADERS.format(container_source=container_source))
        html.append("</thead>")
        html.append("<tbody>")
        for dest_well, well_data in container_info.items():
            html.append(TABLE_ROWS.format(**well_data.dict()))
        html.append("</tbody></table><br><br>")

        ## VISUAL Platemap

        html.append(VISUAL_PLACEMENT_MAP_HEADER)
        html.append("<tbody>")
        html.append(add_wells(container_info))
        html.append("</tbody></table>")
    html.append("</html>")
    html = "".join(html)
    return html


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.sample_udfs(help="Sample UDFs to show in the placement map.")
@options.original_well()
@click.pass_context
def placement_map(ctx, file: str, sample_udfs: List[str], original_well: str):
    """Create a 96 well placement map."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        placement_map_data = get_placement_map_data(lims, process, sample_udfs, original_well)
        html = make_html(placement_map_data, process, original_well)
        with open(f"{file}.html", "w") as file:
            file.write(html)
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
