from cg_lims.exceptions import ZeroReadsError
from genologics.entities import Artifact


class Pool:
    def __init__(self, pool_artifact: Artifact):
        self.total_reads_missing = 0
        self.pool = pool_artifact
        self.artifacts = pool_artifact.input_artifact_list()

    def get_total_reads_missing(self)-> None:
        """Get the total numer of missing reads in the pool"""

        for art in self.artifacts:
            reads = art.samples[0].udf.get('Reads missing (M)')
            if reads is None:
                sys.exit('Missing udfs: Reads missing (M)')
            self.total_reads_missing += reads
        if self.total_reads_missing == 0:
            raise ZeroReadsError(
            "All samples seem to have Missing Reads = 0. You dont want to sequence any of the samples?"
        )


