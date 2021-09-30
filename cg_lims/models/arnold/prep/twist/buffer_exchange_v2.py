from typing import Optional

from genologics.lims import Lims
from pydantic import Field

from cg_lims.models.api.master_steps.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class BufferExchangeArtifactUDFs(BaseStep):
    concentration: Optional[str] = Field(None, alias="Concentration")


class BufferExchangeUDFs(BufferExchangeArtifactUDFs):
    class Config:
        allow_population_by_field_name = True


def get_buffer_exchange_twist(lims: Lims, sample_id: str) -> BufferExchangeUDFs:
    buffer_exchange_twist = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=BufferExchangeArtifactUDFs,
        process_type="Buffer Exchange v2",
    )

    return BufferExchangeUDFs(**buffer_exchange_twist.merge_process_and_artifact_udfs())
