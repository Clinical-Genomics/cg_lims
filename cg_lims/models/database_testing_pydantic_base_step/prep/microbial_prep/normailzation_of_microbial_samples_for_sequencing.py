import logging
from typing import Optional

from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.models.database.prep.base_step import BaseStep


LOG = logging.getLogger(__name__)


class NormalizationOfMicrobialSamplesForSequencingProcessUDFS(BaseModel):
    lot_nr_dilution_buffer_library_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )
    normalized_library_concentration: Optional[float] = Field(
        None, alias="Final Concentration (nM)"
    )
    library_normalization_method: Optional[str] = Field(None, alias="Method document")


class NormalizationOfMicrobialSamplesForSequencing(BaseStep):
    process_type: str = "CG002 - Normalization of microbial samples for sequencing"
    process_udfs = NormalizationOfMicrobialSamplesForSequencingProcessUDFS
