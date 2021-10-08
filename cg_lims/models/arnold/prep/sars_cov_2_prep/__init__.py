from typing import Optional

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
from cg_lims.models.arnold.prep.base_prep import Prep


class SarsCov2Prep(
    Prep,
):
    initial_qc: Optional[AggregateQCDNACovFields]
    pooling_and_cleanup: PoolingAndCleanUpCovFields
    library_prep: LibraryPreparationCovUDFS
    workflow = "Sars-Cov-2"

    class Config:
        allow_population_by_field_name = True
