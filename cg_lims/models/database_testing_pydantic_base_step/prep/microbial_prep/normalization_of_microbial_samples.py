import logging
from typing import Optional

from pydantic.main import BaseModel
from pydantic import Field


from cg_lims.models.database.prep.base_step import BaseStep

LOG = logging.getLogger(__name__)


class NormalizationOfMicrobialSamplesProcessUDFS(BaseModel):
    sample_normalization_method: Optional[str] = Field(None, alias="Method document")
    normalized_sample_concentration: Optional[float] = Field(
        None, alias="Final Concentration (ng/ul)"
    )
    lot_nr_dilution_buffer_sample_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )


class NormalizationOfMicrobialSamples(BaseStep):
    process_type: str = "CG002 - Normalization of microbial samples"
    process_udfs = NormalizationOfMicrobialSamplesProcessUDFS
