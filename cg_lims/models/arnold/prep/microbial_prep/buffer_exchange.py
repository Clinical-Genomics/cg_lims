from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class BufferExchangeArtifactUDF(BaseModel):
    sample_concentration: Optional[float] = Field(None, alias="Concentration")


class BufferExchangeProcessUDFS(BaseModel):
    lot_nr_beads_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Purification Beads")
    lot_nr_etoh_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: EtOH")
    lot_nr_h2o_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Nuclease-free water")
    buffer_exchange_method: Optional[str] = Field(None, alias="Method document")


class BufferExchangeFields(BaseStep):
    process_udfs: BufferExchangeProcessUDFS
    artifact_udfs: BufferExchangeArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_buffer_exchange(lims: Lims, sample_id: str, prep_id: str) -> Optional[BufferExchangeFields]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Buffer Exchange v1",
        optional_step=True,
    )
    if not analyte.artifact:
        return None

    return BufferExchangeFields(
        **analyte.base_fields(),
        process_udfs=BufferExchangeProcessUDFS(**analyte.process_udfs()),
        artifact_udfs=BufferExchangeArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="buffer_exchange",
        workflow="Microbial"
    )
