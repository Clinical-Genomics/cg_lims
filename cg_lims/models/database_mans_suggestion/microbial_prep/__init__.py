from cg_lims.models.database.base_prep import Prep
from cg_lims.models.database.prep.microbial_prep import (
    BufferExchangeProcessUDFS,
    BufferExchangeArtifactUDF,
)
from cg_lims.models.database.prep.microbial_prep.microbial_library_prep_nextera import (
    LibraryPrepNexteraProcessUDFS,
)
from cg_lims.models.database.prep.microbial_prep import (
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
)
from cg_lims.models.database.prep.microbial_prep import (
    NormalizationOfMicrobialSamplesProcessUDFS,
)
from cg_lims.models.database.prep.microbial_prep import (
    PostPCRBeadPurificationProcessUDFS,
    PostPCRBeadPurificationArtifactUDF,
)


class MicrobialPrep(
    Prep,
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
    PostPCRBeadPurificationProcessUDFS,
    PostPCRBeadPurificationArtifactUDF,
    LibraryPrepNexteraProcessUDFS,
    NormalizationOfMicrobialSamplesProcessUDFS,
    BufferExchangeProcessUDFS,
    BufferExchangeArtifactUDF,
):
    workflow = "Microbial"

    class Config:
        allow_population_by_field_name = True
