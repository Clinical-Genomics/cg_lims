from typing import Optional

from .buffer_exchange import (
    BufferExchangeFields,
    BufferExchangeArtifactUDFs,
    get_buffer_exchange_twist,
)
from .capture_and_wash_twist import (
    CaptureandWashFields,
    CaptureandWashProcessUDFs,
    get_capture_and_wash,
)
from .pool_samples_twist import (
    PoolSamplesForHybridizationFields,
    PoolsamplesforhybridizationArtifactUDFs,
    get_pool_samples_twist,
)
from .hybridize_library_twist import (
    HybridizeLibraryTWISTProcessUDFs,
    HybridizeLibraryFields,
    HybridizeLibraryTWISTArtifactUDFs,
    get_hybridize_library_twist,
)
from .bead_purification_twist import (
    BeadPurificationFields,
    BeadPurificationArtifactUDFs,
    get_bead_purification_twist,
)
from .kapa_library_preparation_twist import (
    KAPALibraryPreparationProcessUDFs,
    KAPALibraryPreparationArtifactUDFs,
    KAPALibraryPreparationFields,
    get_kapa_library_preparation_twist,
)
from .aliquot_samples_for_enzymatic_fragmentation_twist import (
    AliquotSamplesForEnzymaticFragmentationFields,
    AliquotSamplesForEnzymaticFragmentationArtifactUdfs,
    AliquotSamplesForEnzymaticFragmentationProcessUdfs,
    get_aliquot_samples_for_enzymatic_fragmentation_udfs,
)

from .amplify_captured_libraries import (
    AmplifycapturedlibrariestwistFields,
    AmplifycapturedlibrariestwistProcessUDFs,
    get_amplify_captured_library_udfs,
)

from .enzymatic_fragmentation_twist import (
    EnzymaticFragmentationTWISTFields,
    EnzymaticFragmentationTWISTProcessUdfs,
    get_enzymatic_fragmentation,
)

from .pre_processing import PreProcessingFields, PreProcessingArtifactUDFs, get_pre_processing_twist

from cg_lims.models.arnold.prep.base_prep import Prep


class TWISTPrep(
    Prep,
):
    pre_processing: Optional[PreProcessingFields]
    pooling: PoolSamplesForHybridizationFields
    library_preparation: KAPALibraryPreparationFields
    hybridize_library: HybridizeLibraryFields
    aliquot_samples_for_enzymatic_fragmentation: AliquotSamplesForEnzymaticFragmentationFields
    amplify_captured_library: AmplifycapturedlibrariestwistFields
    enzymatic_fragmentation: Optional[EnzymaticFragmentationTWISTFields]
    buffer_exchange: Optional[BufferExchangeFields]
    capture_and_wash: CaptureandWashFields
    bead_purification: BeadPurificationFields
    workflow = "TWIST"

    class Config:
        allow_population_by_field_name = True
