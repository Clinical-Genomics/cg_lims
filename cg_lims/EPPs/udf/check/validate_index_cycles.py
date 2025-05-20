import logging
import sys
from typing import List, Optional, Tuple

import click
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process, ReagentType
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_cycle_udf(process: Process, udf_name: str) -> int:
    """Return the number of index cycles for the given UDF name. Defaults to 0 if no value can be found."""
    udf_value: Optional[int] = process.udf.get(udf_name)
    return 0 if not udf_value else udf_value


def get_index_cycles(process: Process) -> Tuple[int, int]:
    """Return the index cycles of a given process."""
    index_1_cycles: int = get_cycle_udf(process=process, udf_name="Index Read 1")
    index_2_cycles: int = get_cycle_udf(process=process, udf_name="Index Read 2")
    return index_1_cycles, index_2_cycles


def validate_per_reagent(process: Process) -> str:
    """Validate the index cycles for the current sequencing set-up. Returns an error message if an issue is found."""
    index_1_cycles, index_2_cycles = get_index_cycles(process=process)
    lane_pools: List[Artifact] = get_artifacts(process=process)
    lims: Lims = process.lims
    failed_index_1_lengths: List[int] = []
    failed_index_2_lengths: List[int] = []
    for pool in lane_pools:
        all_reagents: List[str] = pool.reagent_labels
        for reagent_name in all_reagents:
            reagent: ReagentType = lims.get_reagent_types(name=reagent_name)[0]
            index_sequences: List[str] = reagent.sequence.split("-")
            if len(index_sequences) > 2:
                raise InvalidValueError(
                    f"There can at most be 2 index sequences! Please confirm that index {reagent_name} is valid."
                )
            index_1: str = index_sequences[0] if len(index_sequences) > 0 else ""
            index_2: str = index_sequences[1] if len(index_sequences) > 1 else ""
            if len(index_1) > index_1_cycles:
                failed_index_1_lengths.append(len(index_1))
                LOG.info(
                    f"Reagent '{reagent_name}': Index 1 length ({len(index_1)}) "
                    f"exceeds the set index cycles ({index_1_cycles})."
                )
            if len(index_2) > index_2_cycles:
                failed_index_2_lengths.append(len(index_2))
                LOG.info(
                    f"Reagent '{reagent_name}': Index 2 length ({len(index_2)}) "
                    f"exceeds the set index cycles ({index_2_cycles})."
                )
    message: List[str] = []
    if failed_index_1_lengths:
        message.append(
            f"Index 1 cycles ({index_1_cycles}) are insufficient for "
            f"the longest index 1 sequence ({max(failed_index_1_lengths)})."
        )
    if failed_index_2_lengths:
        message.append(
            f"Index 2 cycles ({index_2_cycles}) are insufficient for "
            f"the longest index 2 sequence ({max(failed_index_2_lengths)})."
        )
    return " ".join(message)


@click.command()
@click.pass_context
def validate_index_cycles(ctx):
    """Script to validate that the number of index cycles assigned in
    the NovaSeq sequencing set-up is enough for all indexes."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        error_message: str = validate_per_reagent(process=process)
        if error_message:
            LOG.error(error_message)
            raise InvalidValueError(
                "Error: "
                + error_message
                + " Please alter the sequencing settings accordingly. See the log for further details."
            )
        LOG.info("The sequencing settings passed validation.")
        click.echo("The sequencing settings passed validation.")
    except LimsError as e:
        sys.exit(e.message)
