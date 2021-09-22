import logging
from typing import Optional

from genologics.lims import Lims, Artifact
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.get.artifacts import get_latest_artifact

LOG = logging.getLogger(__name__)


class BufferExchangeArtifactUDF(BaseModel):
    sample_concentration: Optional[float] = Field(None, alias="Concentration")


class BufferExchangeProcessUDFS(BaseModel):
    lot_nr_beads_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Purification Beads")
    lot_nr_etoh_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: EtOH")
    lot_nr_h2o_buffer_exchange: Optional[str] = Field(None, alias="Lot Nr: Nuclease-free water")
    buffer_exchange_method: Optional[str] = Field(None, alias="Method document")


class BufferExchangeUDFS(BufferExchangeProcessUDFS, BufferExchangeArtifactUDF):
    class Config:
        allow_population_by_field_name = True


def get_buffer_exchange_artifact_udfs(artifact: Artifact) -> BufferExchangeArtifactUDF:
    artifact_udfs = dict(artifact.udf.items())
    return BufferExchangeArtifactUDF(**artifact_udfs)


def get_buffer_exchange_process_udfs(artifact: Artifact) -> BufferExchangeProcessUDFS:
    process_udfs = dict(artifact.parent_process.udf.items())
    return BufferExchangeProcessUDFS(**process_udfs)


def get_buffer_exchange_udfs(lims: Lims, sample_id: str) -> BufferExchangeUDFS:
    process_type = "Buffer Exchange v1"

    artifact: Artifact = get_latest_artifact(
        lims=lims, sample_id=sample_id, process_type=[process_type]
    )

    buffer_exchange_artifact_udfs: BufferExchangeArtifactUDF = get_buffer_exchange_artifact_udfs(
        artifact=artifact
    )
    buffer_exchange_process_udfs: BufferExchangeProcessUDFS = get_buffer_exchange_process_udfs(
        artifact=artifact
    )

    # Merging artifact udfs and process udfs
    buffer_exchange_udfs = buffer_exchange_process_udfs.dict(exclude_none=True)
    buffer_exchange_udfs.update(buffer_exchange_artifact_udfs.dict(exclude_none=True))
    return BufferExchangeUDFS(**buffer_exchange_udfs)
