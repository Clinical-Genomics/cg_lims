"""Base cg_lims calss definitions
"""

from genologics.entities import Artifact

from cg_lims.exceptions import MissingUDFsError, ZeroReadsError


class Pool:
    """Collecting informatiuon general to any pool"""

    def __init__(self, pool_artifact: Artifact):
        self.total_reads_missing = 0
        self.artifact = pool_artifact

    def get_total_reads_missing(self) -> None:
        """Get the total numer of missing reads in the pool"""

        for art in self.artifact.input_artifact_list():
            reads = art.samples[0].udf.get("Reads missing (M)")
            if reads is None:
                raise MissingUDFsError("Missing udfs: Reads missing (M)")
            self.total_reads_missing += reads
        if self.total_reads_missing == 0:
            raise ZeroReadsError("All samples seem to have Missing Reads = 0!")
