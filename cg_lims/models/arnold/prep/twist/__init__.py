from typing import List

from genologics.lims import Lims

from .buffer_exchange import (
    BufferExchangeFields,
    BufferExchangeArtifactUDFs,
    get_buffer_exchange_twist,
)
from .capture_and_wash_twist import (
    CaptureandWashFields,
    CaptureAndWashProcessUDFs,
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
    get_aliquot_samples_for_enzymatic_fragmentation,
)

from .amplify_captured_libraries import (
    AmplifycapturedLibrariestwistFields,
    AmplifycapturedLibrariestwistProcessUDFs,
    get_amplify_captured_library_udfs,
)

from .enzymatic_fragmentation_twist import (
    EnzymaticFragmentationTWISTFields,
    EnzymaticFragmentationTWISTProcessUdfs,
    get_enzymatic_fragmentation,
)

from .reception_control import (
    SampleArtifactUDF,
    SampleArtifactFields,
    get_sample_artifact_fields,
)
from ..base_step import BaseStep


def build_twist_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""
    prep_id = f"{sample_id}_{process_id}"
    step_documents = [
        get_aliquot_samples_for_enzymatic_fragmentation(
            sample_id=sample_id, lims=lims, prep_id=prep_id
        ),
        get_hybridize_library_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_pool_samples_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_capture_and_wash(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_kapa_library_preparation_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_buffer_exchange_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_bead_purification_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_enzymatic_fragmentation(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_amplify_captured_library_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_sample_artifact_fields(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]
    return [document for document in step_documents if document is not None]
