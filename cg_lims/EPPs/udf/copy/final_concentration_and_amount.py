import subprocess
import sys
import click
from genologics.entities import Artifact
from genologics.lims import Lims

from cg_lims import options
from cg_lims.get.artifacts import get_latest_artifact
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts
import logging

LOG = logging.getLogger(__name__)


def get_final_conc_and_amount_dna(
    concentration_art: Artifact,
    lims: Lims,
    amount_udf: str,
    concentration_udf: str,
    amount_step: str,
) -> None:
    sample = get_one_sample_from_artifact(artifact=concentration_art)
    sample_id = sample.id

    amount_art = None
    step = concentration_art.parent_process
    # Go back in history until we get to an output artifact from the amount_step
    while step and not amount_art:
        art = get_latest_artifact(lims=lims, sample_id=sample_id, process_type=step.type.name)
        processes = [p.type.name for p in lims.get_processes(inputartifactlimsid=art.id)]
        for step in amount_step:
            if step in processes:
                amount_art = art
                break
        step = art.parent_process

    sample.udf["lucigen_amount"] = amount_art.udf.get(amount_udf) if amount_art else None
    sample.udf["lucigen_concentration"] = concentration_art.udf.get(concentration_udf)
    sample.put()


@click.command()
@options.concantration_udf()
@options.amount_udf()
@options.process_type(help="Process from where to fetch the Amount")
@click.pass_context
def lucigen_conc_and_amount_to_sample(
    ctx, process_type: str, amount_udf: str, concentration_udf: str
) -> None:
    """Run from within a concentration step.

    Getting concentration from concentration step and then going back
    in history to the latest amount_step to get the amount.

    Saving concentration and amount to Sample UDFs:"""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    try:
        artifacts = get_artifacts(process=process, input=False)  ##in or out?
        for artifact in artifacts:
            get_final_conc_and_amount_dna(
                concentration_art=artifact,
                lims=lims,
                amount_step=process_type,
                amount_udf=amount_udf,
                concentration_udf=concentration_udf,
            )
        LOG.info("Udfs have been set on all samples.")
    except LimsError as e:
        LOG.error(e.message)


@click.command()
@options.concantration_udf()
@options.amount_udf()
@options.process_type(help="Process from where to fetch the Amount")
@click.pass_context
def lucigen_conc_and_amount_to_sample_with_sub_process(
    ctx, process_type: str, amount_udf: str, conc_udf: str
) -> None:
    """"""

    config_path = ctx.obj["config_path"]
    log_path = ctx.obj["log_path"]
    process_id = ctx.obj["process"].id

    command_line = [
        "lims",
        "-c",
        config_path,
        "epps",
        "-l",
        log_path,
        "-p",
        process_id,
        "udf",
        "copy",
        "lucigen-conc-and-amount-to-sample",
        "--conc-udf",
        conc_udf,
        "--amount-udf",
        amount_udf,
        "--process-type",
        process_type,
    ]
