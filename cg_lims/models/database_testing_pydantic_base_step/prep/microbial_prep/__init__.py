from cg_lims.models.database.prep.base_prep import Prep
from .microbial_library_prep_nextera import (
    MicrobialLibraryPrepNexteraProcessUDFS,
    MicrobialLibraryPrepNextera,
)
from .normalization_of_microbial_samples import (
    NormalizationOfMicrobialSamplesProcessUDFS,
    NormalizationOfMicrobialSamples,
)
from .normailzation_of_microbial_samples_for_sequencing import (
    NormalizationOfMicrobialSamplesForSequencing,
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
)
from .buffer_exchange import BufferExchange, BufferExchangeArtifactUDF, BufferExchangeProcessUDFS
from .post_pcr_bead_purification import (
    PostPCRBeadPurificationArtifactUDF,
    PostPCRBeadPurificationProcessUDFS,
    PostPCRBeadPurification,
)


class MicrobialPrep(
    Prep,
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
    PostPCRBeadPurificationProcessUDFS,
    PostPCRBeadPurificationArtifactUDF,
    MicrobialLibraryPrepNexteraProcessUDFS,
    NormalizationOfMicrobialSamplesProcessUDFS,
    BufferExchangeProcessUDFS,
    BufferExchangeArtifactUDF,
):
    workflow = "Microbial"

    class Config:
        allow_population_by_field_name = True
