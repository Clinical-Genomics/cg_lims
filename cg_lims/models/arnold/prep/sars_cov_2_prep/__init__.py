from typing import List

from genologics.lims import Lims

from .library_preparation import (
    LibraryPreparationCovUDFS,
    get_library_prep_cov_udfs,
    LibraryPreparationCovProcessUDFS,
)
from .pooling_and_cleanup import (
    PoolingAndCleanUpCovProcessUDFS,
    PoolingAndCleanUpCovArtifactUDF,
    PoolingAndCleanUpCovFields,
    get_pooling_and_cleanup_udfs,
)
from .aggregate_qc import (
    AggregateQCDNACovFields,
    AggregateQCDNACovArtifactUDF,
    get_aggregate_qc_dna_cov_udfs,
)
from ..base_step import BaseStep


def build_sars_cov_2_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""
    prep_id = f"{sample_id}_{process_id}"
    return [
        get_pooling_and_cleanup_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_library_prep_cov_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_aggregate_qc_dna_cov_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]
