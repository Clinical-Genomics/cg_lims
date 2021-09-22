import logging
from typing import Optional

from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.database.prep.base_step import BaseStep

LOG = logging.getLogger(__name__)


class BufferExchangeArtifactUDF(BaseModel):
    sample_concentration: Optional[float] = Field(None, alias="Concentration")


class BufferExchangeProcessUDFS(BaseModel):
    lot_nr_beads_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Purification Beads")
    lot_nr_etoh_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: EtOH")
    lot_nr_h2o_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Nuclease-free water")
    buffer_exchange_method: Optional[str] = Field(None, alias="Method document")


class BufferExchange(BaseStep):
    process_type: str = "Buffer Exchange v"
    process_udfs = BufferExchangeProcessUDFS
    artifact_udfs = BufferExchangeArtifactUDF
