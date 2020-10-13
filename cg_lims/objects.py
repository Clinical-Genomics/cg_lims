

class Pool:
    def __init__(self, pool_artifact):
        self.total_reads = 0
        self.pool = pool_artifact
        self.artifacts = pool_artifact.input_artifact_list()

    def get_total_reads(self):
        """Get the total numer of missing reads in the pool"""

        for art in self.artifacts:
            reads = art.samples[0].udf.get('Reads missing (M)')
            if reads is None:
                sys.exit('Missing udfs: Reads missing (M)')
            self.total_reads += reads
        if self.total_reads == 0:
            sys.exit('All samples seem to have Missing Reads = 0. You dont want to sequence any of the samples?')


