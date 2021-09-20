from cg_lims.models.database.base_prep import Prep
from cg_lims.models.database.microbial_prep.buffer_exchange import (
    BufferExchangeProcessUDFS,
    BufferExchangeArtifactUDF,
)
from cg_lims.models.database.microbial_prep.microbial_library_prep_nextera import (
    MicrobialLibraryPrepNexteraProcessUDFS,
)
from cg_lims.models.database.microbial_prep.normailzation_of_microbial_samples_for_sequencing import (
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
)
from cg_lims.models.database.microbial_prep.normalization_of_microbial_samples import (
    NormalizationOfMicrobialSamplesProcessUDFS,
)
from cg_lims.models.database.microbial_prep.post_pcr_bead_purification import (
    PostPCRBeadPurificationProcessUDFS,
    PostPCRBeadPurificationArtifactUDF,
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
