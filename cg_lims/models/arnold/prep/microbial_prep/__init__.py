from typing import Optional

from .microbial_library_prep_nextera import (
    LibraryPrepNexteraProcessUDFS,
    LibraryPrepFields,
    get_library_prep_nextera,
)
from .normalization_of_microbial_samples import (
    NormalizationProcessUDFS,
    NormalizationFields,
    get_normalization_of_mictobial_samples,
)
from .buffer_exchange import (
    BufferExchangeProcessUDFS,
    BufferExchangeArtifactUDF,
    BufferExchangeFields,
    get_buffer_exchange,
)
from .normailzation_of_microbial_samples_for_sequencing import (
    NormalizationForSequencingFields,
    NormalizationOfSamplesForSequencingProcessUDFS,
    get_normalization_of_samples,
)
from .post_pcr_bead_purification import (
    PostPCRBeadPurificationFields,
    PostPCRBeadPurificationArtifactUDF,
    PostPCRBeadPurificationProcessUDFS,
    get_post_bead_pcr_purification,
)
from cg_lims.models.arnold.prep.base_prep import Prep


class MicrobialPrep(Prep):
    normalization_of_samples_for_sequencing: NormalizationForSequencingFields
    post_bead_pcr_purification: PostPCRBeadPurificationFields
    library_prep: LibraryPrepFields
    normalization_of_mictobial_samples: NormalizationFields
    buffer_exchange: Optional[BufferExchangeFields]
    workflow = "Microbial"

    class Config:
        allow_population_by_field_name = True
