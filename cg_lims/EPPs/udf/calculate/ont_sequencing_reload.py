import logging
import sys
from typing import List

import click
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims.get.udfs import get_analyte_udf
from genologics.entities import Artifact, Process
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_concentration_after_prep(lims: Lims, sample_id: str) -> float:
    """Return sample concentration after ONT library prep."""
    return get_analyte_udf(
        lims=lims, sample_id=sample_id, process_types=["ONT Start Sequencing"], udf="Concentration"
    )


def get_total_amount_after_prep(lims: Lims, sample_id: str) -> float:
    """Return total sample amount (fmol) after ONT library prep."""
    return get_analyte_udf(
        lims=lims, sample_id=sample_id, process_types=["ONT Start Sequencing"], udf="Amount (fmol)"
    )


def get_loading_amount(lims: Lims, sample_id: str) -> float:
    """Return the original loading amount of the flow cell."""
    return get_analyte_udf(
        lims=lims,
        sample_id=sample_id,
        process_types=["ONT Start Sequencing"],
        udf="Loading Amount (fmol)",
    )


def get_reload_amounts(lims: Lims, sample_id: str) -> List[float]:
    """Return any potential reloading amounts of the flow cell."""
    result_files = lims.get_artifacts(
        process_type="ONT Sequencing and Reloading v2", samplelimsid=sample_id, type="ResultFile"
    )
    amounts = []
    for result_file in result_files:
        if result_file.name == "EPP Log":
            continue
        else:
            reload_amount = result_file.udf.get("Reload Amount (fmol)")
            if not reload_amount:
                reload_amount = 0
            amounts.append(reload_amount)
    return amounts


def get_available_amount(lims: Lims, sample_id: str) -> float:
    """Return the available sample amount (fmol) after the original loading and any potential reloads."""
    original_amount = get_total_amount_after_prep(lims=lims, sample_id=sample_id)
    loading_amount = get_loading_amount(lims=lims, sample_id=sample_id)
    total_reload_amount = sum(get_reload_amounts(lims=lims, sample_id=sample_id))
    return original_amount - loading_amount - total_reload_amount


def set_available_amount_and_conc(lims: Lims, artifact: Artifact) -> None:
    """Set the available amount and concentration of the sample."""
    sample_id = get_one_sample_from_artifact(artifact=artifact).id
    concentration = get_concentration_after_prep(lims=lims, sample_id=sample_id)
    available_amount = get_available_amount(lims=lims, sample_id=sample_id)
    artifact.udf["Concentration"] = concentration
    artifact.udf["Available Amount (fmol)"] = available_amount
    artifact.put()


@click.command()
@click.pass_context
def ont_available_sequencing_reload(ctx):
    """Calculates and sets the amount of material available for reload of ONT runs."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims: Lims = ctx.obj["lims"]
    process: Process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, measurement=True)
        for artifact in artifacts:
            set_available_amount_and_conc(lims=lims, artifact=artifact)
        message: str = "Available amounts have been successfully calculated and set."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
