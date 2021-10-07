from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte


## optional step! så kolla var hämta concentraion annars


class BufferExchangeArtifactUDFs(BaseModel):
    buffer_exchange_concentration: Optional[str] = Field(None, alias="Concentration")


class BufferExchangeUDFs(BufferExchangeArtifactUDFs):
    buffer_exchange_well_position: Optional[str] = Field(None, alias="well_position")
    buffer_exchange_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_buffer_exchange_twist(lims: Lims, sample_id: str) -> BufferExchangeUDFs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=BufferExchangeArtifactUDFs,
        process_type="Buffer Exchange v2",
        optional_step=True,
    )

    return BufferExchangeUDFs(
        **analyte.merge_analyte_fields(),
    )
