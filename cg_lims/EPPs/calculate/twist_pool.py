
from cg_lims.objects import Pool


class TwistPool(Pool):
    def __init__(self):
        self.pool.qc_flag='PASSED'
        self.total_volume = 0
        self.amount_fail = False

    def calculate_amount_and_volume(self):
        """Perform calcualtions for the input artifacts to the pool"""

        for art in self.artifacts:
            reads = art.samples[0].udf.get('Reads missing (M)')
            concentration = art.udf.get('Concentration')
            fract_of_pool = reads/float(self.total_reads)
            amount_to_pool = self.pool.udf.get('Total Amount (ng)') * fract_of_pool
            vol = amount_to_pool/concentration
            if amount_to_pool > art.udf.get('Amount (ng)') or amount_to_pool < 187.5:
                self.pool.qc_flag='FAILED'
                self.amount_fail = True
            art.udf['Amount taken (ng)'] = amount_to_pool
            art.udf['Volume of sample (ul)'] = vol
            art.put()
            self.total_volume += vol    


def calculate_volumes_for_pooling(pools):
    """Perform calculations for each pool in the step"""
    okej = 0
    failed = 0
    amount_fail = True
    all_volumes= []
    for pool_art in pools:
        pool = TwistPool(pool_artifact = pool_art)
        pool.get_total_reads()
        pool.calculate_amount_and_volume()
        if pool.amount_fail:
            amount_fail = True
        if pool.total_volume:
            pool_art.udf['Total Volume (ul)'] = pool.total_volume
            all_volumes.append(pool.total_volume)
            okej +=1
        else:
            failed +=1
    return all_volumes

def calculate_volume_wather(pools, all_volumes):
    """Perform wather calculations for each pool in the step"""

    for pool_art in pools:
        if pool_art.udf.get('Total Volume (ul)'):
            pool_art.udf['Volume H2O (ul)'] = max(all_volumes) - pool_art.udf.get('Total Volume (ul)')
        pool_art.put()


@click.command()
@click.pass_context
def twist_pool(ctx):
    """"""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    pools = get_artifacts(process=process, input=False)
    all_volumes = calculate_volumes_for_pooling(pools)
    calculate_volume_wather(pools, all_volumes)

