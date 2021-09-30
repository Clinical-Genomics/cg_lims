from .microbial_library_prep_nextera import (
    LibraryPrepNexteraProcessUDFS,
    LibraryPrepUDFS,
    get_library_prep_nextera_udfs,
)
from .normalization_of_microbial_samples import (
    NormalizationOfMicrobialSamplesProcessUDFS,
    NormalizationOfMicrobialSamplesUDFS,
    get_normalization_of_mictobial_samples_udfs,
)
from .buffer_exchange import (
    BufferExchangeProcessUDFS,
    BufferExchangeArtifactUDF,
    BufferExchangeUDFS,
    get_buffer_exchange_udfs,
)
from .normailzation_of_microbial_samples_for_sequencing import (
    NormalizationOfSamplesForSequencingUDFS,
    NormalizationOfSamplesForSequencingProcessUDFS,
    get_normalization_of_samples_for_sequencing_udfs,
)
from .post_pcr_bead_purification import (
    PostPCRBeadPurificationUDF,
    PostPCRBeadPurificationArtifactUDF,
    PostPCRBeadPurificationProcessUDFS,
    get_post_bead_pcr_purification_udfs,
)
from cg_lims.models.arnold.prep.base_prep import Prep


class MicrobialPrep(
    Prep,
    NormalizationOfSamplesForSequencingUDFS,
    PostPCRBeadPurificationUDF,
    LibraryPrepUDFS,
    NormalizationOfMicrobialSamplesUDFS,
    BufferExchangeUDFS,
):
    workflow = "Microbial"

    class Config:
        allow_population_by_field_name = True
