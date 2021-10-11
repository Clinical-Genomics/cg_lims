from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte

from cg_lims.models.arnold.prep.base_step import BaseStep


class BufferExchangeArtifactUDFs(BaseModel):
    buffer_exchange_concentration: Optional[str] = Field(None, alias="Concentration")


class BufferExchangeFields(BaseStep):
    artifact_udfs: BufferExchangeArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_buffer_exchange_twist(lims: Lims, sample_id: str, prep_id: str) -> BufferExchangeFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Buffer Exchange v2",
        optional_step=True,
    )

    return BufferExchangeFields(
        **analyte.base_fields(),
        artifact_udfs=BufferExchangeArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="buffer_exchange",
        workflow="TWIST",
    )
