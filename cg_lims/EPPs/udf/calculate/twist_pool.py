
from cg_lims.objects import Pool

import click

class TwistPool(Pool):
    def __init__(self):
        self.pool.qc_flag='PASSED'
        self.total_volume = 0
        self.amount_fail = False

    def calculate_amount_and_volume(self):
        """Perform calcualtions for the input artifacts to the pool.
        Based on the udf 'Reads missing (M)', the sample is given an 
        equivalent proportion in the pool.

        The total avalible volume of a sample is allways 15.

        A sample should not have les than 187.5 ng in the pool
        """

        for art in self.artifacts:
            reads = art.samples[0].udf.get('Reads missing (M)')
            concentration = art.udf.get('Concentration')
            fract_of_pool = reads/float(self.total_reads)
            amount_to_pool = self.pool.udf.get('Total Amount (ng)') * fract_of_pool
            vol = amount_to_pool/concentration
            if vol > 15:
                vol = 15
            if amount_to_pool > art.udf.get('Amount (ng)') or amount_to_pool < 187.5:
                self.pool.qc_flag='FAILED'
                self.amount_fail = True
            art.udf['Amount taken (ng)'] = amount_to_pool
            art.udf['Volume of sample (ul)'] = vol
            art.put()
            self.total_volume += vol



def calculate_volumes_for_pooling(pools):
    """Perform calculations for each pool in the step.
    All pools in the plate must have the same volume to not overdry.
    Wahter is added to each pool, for them to all get the same volume."""

    amount_failed_for_some_pool = False
    all_volumes= []

    for pool_art in pools:
        pool = TwistPool(pool_artifact = pool_art)
        pool.get_total_reads()
        pool.calculate_amount_and_volume()
        if pool.amount_fail:
            amount_failed_for_some_pool = True
        if pool.total_volume:
            pool_art['Total Volume (ul)'] = pool.total_volume
        all_volumes.append(pool.total_volume)

    for pool_art in pools:
        if pool_art.udf.get('Total Volume (ul)'):
            pool_art.udf['Volume H2O (ul)'] = max(all_volumes) - pool_art.udf.get('Total Volume (ul)')
        pool_art.put()
    
    if amount_failed_for_some_pool:
        raise LowAmountError(
            'Input amount low for samples in some pool. Generate placement map for more info.'
        )



@click.command()
@click.pass_context
def twist_pool(ctx):
    """Calculates volumes for pools in a plate before hybridization."""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        pools = get_artifacts(process=process, input=False)
        calculate_volumes_for_pooling(pools)
    except LimsError as e:
        sys.exit(e.message)

