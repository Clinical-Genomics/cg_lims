import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import LimsError, LowAmountError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.objects import Pool

LOG = logging.getLogger(__name__)


# The avalible volume of a sample is allways 15.
AVALIBLE_SAMPLE_VOLUME = 15

# A sample should not have les than 187.5 ng in the pool
MINIMUM_SAMPLE_AMOUNT = 187.5


class TwistPool(Pool):
    def __init__(self, artifact: Artifact):
        super().__init__(artifact)
        self.qc_flag = "PASSED"
        self.total_volume = 0
        self.amount_fail = False

    def calculate_amount_and_volume(self):
        """Perform calcualtions for the input artifacts to the pool.
        Based on the udf 'Reads missing (M)', the sample is given an
        equivalent proportion in the pool.
        """

        for art in self.artifact.input_artifact_list():
            reads = art.samples[0].udf.get("Reads missing (M)")
            concentration = art.udf.get("Concentration")
            total_amount = self.artifact.udf.get("Total Amount (ng)")
            if None in [reads, concentration, total_amount]:
                self.qc_flag = "FAILED"
                self.amount_fail = True
                continue
            fract_of_pool = reads / float(self.total_reads_missing)
            amount_to_pool = total_amount * fract_of_pool
            vol = amount_to_pool / concentration
            if vol > AVALIBLE_SAMPLE_VOLUME:
                vol = AVALIBLE_SAMPLE_VOLUME
            self.total_volume += vol
            art.udf["Amount taken (ng)"] = amount_to_pool
            art.udf["Volume of sample (ul)"] = vol
            art.put()
            if (
                amount_to_pool > art.udf.get("Amount (ng)")
                or amount_to_pool < MINIMUM_SAMPLE_AMOUNT
            ):
                self.qc_flag = "FAILED"
                self.amount_fail = True


def calculate_volumes_for_pooling(pools: List[Artifact]):
    """Perform calculations for each pool in the step.
    All pools in the plate must have the same volume to not overdry.
    Wahter is added to each pool for them to all get the same volume."""

    amount_failed_for_some_pool = False
    all_volumes = []

    for pool_art in pools:
        twist_pool = TwistPool(pool_art)
        twist_pool.get_total_reads_missing()
        twist_pool.calculate_amount_and_volume()
        pool_art.qc_flag = twist_pool.qc_flag
        if twist_pool.amount_fail:
            amount_failed_for_some_pool = True
        if twist_pool.total_volume:
            pool_art.udf["Total Volume (ul)"] = twist_pool.total_volume
        all_volumes.append(twist_pool.total_volume)

    for pool_art in pools:
        if pool_art.udf.get("Total Volume (ul)"):
            pool_art.udf["Volume H2O (ul)"] = max(all_volumes) - pool_art.udf.get(
                "Total Volume (ul)"
            )
        pool_art.put()

    if amount_failed_for_some_pool:
        raise LowAmountError(
            "Input amount low for samples in some pool or udfs missing. Generate placement map for more info."
        )


@click.command()
@click.pass_context
def twist_pool(ctx):
    """Calculates volumes for pools in a plate before hybridization."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    try:
        pools = get_artifacts(process=process, input=False)
        calculate_volumes_for_pooling(pools)
    except LimsError as e:
        sys.exit(e.message)
