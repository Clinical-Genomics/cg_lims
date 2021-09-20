import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.database.base_prep import BasePrep

LOG = logging.getLogger(__name__)


class BufferExchange(BasePrep):
    def __init__(self, lims: Lims, sample_id: str):
        super().__init__(lims=lims, sample_id=sample_id)
        self.process_type = "Buffer Exchange v1"
        self.artifact_udf_model = BufferExchangeArtifactUDF
        self.process_udf_model = BufferExchangeProcessUDFS
        self.artifact = self.set_artifact()
        self.optional_step = True


class BufferExchangeArtifactUDF(BaseModel):
    sample_concentration: Optional[float] = Field(None, alias="Concentration")


class BufferExchangeProcessUDFS(BaseModel):
    lot_nr_beads_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Purification Beads")
    lot_nr_etoh_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: EtOH")
    lot_nr_h2o_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Nuclease-free water")
    buffer_exchange_method: Optional[str] = Field(None, alias="Method document")
