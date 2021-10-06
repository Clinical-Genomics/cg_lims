from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


class BufferExchangeArtifactUDF(BaseModel):
    sample_concentration: Optional[float] = Field(None, alias="Concentration")


class BufferExchangeProcessUDFS(BaseModel):
    lot_nr_beads_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Purification Beads")
    lot_nr_etoh_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: EtOH")
    lot_nr_h2o_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Nuclease-free water")
    buffer_exchange_method: Optional[str] = Field(None, alias="Method document")


class BufferExchangeUDFS(BufferExchangeProcessUDFS, BufferExchangeArtifactUDF):
    a_well_position: Optional[str] = Field(None, alias="well_position")
    a_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_buffer_exchange_udfs(lims: Lims, sample_id: str) -> BufferExchangeUDFS:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=BufferExchangeProcessUDFS,
        artifact_udf_model=BufferExchangeArtifactUDF,
        process_type="Buffer Exchange v1",
        optional_step=True,
    )

    return BufferExchangeUDFS(
        **analyte.merge_analyte_fields(),
    )
