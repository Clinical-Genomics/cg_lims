import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field


from cg_lims.models.database.base_prep import BasePrep

LOG = logging.getLogger(__name__)


class NormalizationOfMicrobialSamples(BasePrep):
    def __init__(self, lims: Lims, sample_id: str):
        super().__init__(lims=lims, sample_id=sample_id)
        self.process_type = "CG002 - Normalization of microbial samples"
        self.process_udf_model = NormalizationOfMicrobialSamplesProcessUDFS
        self.artifact = self.set_artifact()


class NormalizationOfMicrobialSamplesProcessUDFS(BaseModel):
    sample_normalization_method: Optional[str] = Field(None, alias="Method document")
    normalized_sample_concentration: Optional[float] = Field(
        None, alias="Final Concentration (ng/ul)"
    )
    lot_nr_dilution_buffer_sample_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )
