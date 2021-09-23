import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte

LOG = logging.getLogger(__name__)


class PostPCRBeadPurificationProcessUDFS(BaseModel):
    lot_nr_beads_library_prep: str = Field(..., alias="Lot nr: Beads")
    lot_nr_etoh_library_prep: str = Field(..., alias="Lot nr: EtOH")
    lot_nr_h2o_library_prep: str = Field(..., alias="Lot nr: H2O")


class PostPCRBeadPurificationArtifactUDF(BaseModel):
    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")
    finished_library_average_size: float = Field(..., alias="Average Size (bp)")


class PostPCRBeadPurificationUDF(
    PostPCRBeadPurificationProcessUDFS, PostPCRBeadPurificationArtifactUDF
):
    class Config:
        allow_population_by_field_name = True


def get_post_bead_pcr_purification_udfs(lims: Lims, sample_id: str) -> PostPCRBeadPurificationUDF:
    microbial_library_prep = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=PostPCRBeadPurificationProcessUDFS,
        artifact_udf_model=PostPCRBeadPurificationArtifactUDF,
        process_type="Post-PCR bead purification v1",
    )

    return PostPCRBeadPurificationUDF(**microbial_library_prep.merge_process_and_artifact_udfs())
