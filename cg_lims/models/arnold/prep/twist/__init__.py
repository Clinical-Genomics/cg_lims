from .buffer_exchange import (
    BufferExchangeUDFs,
    BufferExchangeArtifactUDFs,
    get_buffer_exchange_twist,
)
from .capture_and_wash_twist import (
    CaptureandWashUDFs,
    CaptureandWashProcessUDFs,
    get_capture_and_wash,
)
from .pool_samples_twist import (
    PoolsamplesforhybridizationUDFs,
    PoolsamplesforhybridizationArtifactUDFs,
    get_pool_samples_twist,
)
from .hybridize_library_twist import (
    HybridizeLibraryTWISTProcessUDFs,
    HybridizeLibraryUDFs,
    HybridizeLibraryTWISTArtifactUDFs,
    get_hybridize_library_twist,
)
from .bead_purification_twist import (
    BeadPurificationUDFs,
    BeadPurificationArtifactUDFs,
    get_bead_purification_twist,
)
from .kapa_library_preparation_twist import (
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

from .amplify_captured_libraries import (
    AmplifycapturedlibrariestwistUDFs,
    AmplifycapturedlibrariestwistProcessUDFs,
    get_amplify_captured_library_udfs,
)

from .enzymatic_fragmentation_twist import (
    EnzymaticFragmentationTWISTUdfs,
    EnzymaticFragmentationTWISTProcessUdfs,
    get_enzymatic_fragmentation,
)

from .pre_processing import PreProcessingUDFs, PreProcessingArtifactUDFs, get_pre_processing_twist

from cg_lims.models.arnold.prep.base_prep import Prep


class TWISTPrep(
    Prep,
    PoolsamplesforhybridizationUDFs,
    HybridizeLibraryUDFs,
    KAPALibraryPreparationUDFs,
    AliquotSamplesForEnzymaticFragmentationUdfs,
    AmplifycapturedlibrariestwistUDFs,
    EnzymaticFragmentationTWISTUdfs,
    BufferExchangeUDFs,
    CaptureandWashUDFs,
    BeadPurificationUDFs,
    PreProcessingUDFs,
):
    workflow = "TWIST"

    class Config:
        allow_population_by_field_name = True
