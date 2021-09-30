from .buffer_exchange_v2 import (
    BufferExchangeUDFs,
    BufferExchangeArtifactUDFs,
    get_buffer_exchange_twist,
)
from .capture_and_wash_twist_v2 import (
    CaptureandWashUDFs,
    CaptureandWashProcessUDFs,
    get_capture_and_wash,
)
from .pool_samples_twist_v2 import (
    PoolsamplesforhybridizationUDFs,
    PoolsamplesforhybridizationArtifactUDFs,
    get_pool_samples_twist,
)
from .hybridize_library_twist_v2 import (
    HybridizeLibraryTWISTProcessUDFs,
    HybridizeLibraryUDFs,
    HybridizeLibraryTWISTArtifactUDFs,
    get_hybridize_library_twist,
)
from .bead_purification_twist_v2 import (
    BeadPurificationUDFs,
    BeadPurificationArtifactUDFs,
    get_bead_purification_twist,
)
from .kapa_library_preparation_twist_v1 import (
    KAPALibraryPreparationProcessUDFs,
    KAPALibraryPreparationArtifactUDFs,
    KAPALibraryPreparationUDFs,
    get_kapa_library_preparation_twist,
)
from .aliquot_samples_for_enzymatic_fragmentation_twist import (
    AliquotSamplesForEnzymaticFragmentationUdfs,
    AliquotSamplesForEnzymaticFragmentationArtifactUdfs,
    AliquotSamplesForEnzymaticFragmentationProcessUdfs,
    get_aliquot_samples_for_enzymatic_fragmentation_udfs,
)

from cg_lims.models.database.prep.base_prep import Prep


class SarsCov2Prep(
    Prep,
    PoolsamplesforhybridizationUDFs,
    HybridizeLibraryUDFs,
    KAPALibraryPreparationUDFs,
    AliquotSamplesForEnzymaticFragmentationUdfs,
    BufferExchangeUDFs,
    CaptureandWashUDFs,
    BeadPurificationUDFs,
):
    workflow = "TWIST"

    class Config:
        allow_population_by_field_name = True
