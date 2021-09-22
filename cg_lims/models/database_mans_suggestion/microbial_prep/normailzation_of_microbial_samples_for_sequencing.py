import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field


from cg_lims.models.database.base_prep import BasePrep

LOG = logging.getLogger(__name__)


class NormalizationOfMicrobialSamplesForSequencing(BasePrep):
    def __init__(self, lims: Lims, sample_id: str):
        super().__init__(lims=lims, sample_id=sample_id)
        self.process_type = "CG002 - Normalization of microbial samples for sequencing"
        self.process_udf_model = NormalizationOfMicrobialSamplesForSequencingProcessUDFS
        self.artifact = self.set_artifact()


class NormalizationOfMicrobialSamplesForSequencingProcessUDFS(BaseModel):
    lot_nr_dilution_buffer_library_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )
    normalized_library_concentration: Optional[float] = Field(
        None, alias="Final Concentration (nM)"
    )
    library_normalization_method: Optional[str] = Field(None, alias="Method document")
