import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.objects import BaseAnalyte

LOG = logging.getLogger(__name__)


class PostPCRBeadPurificationProcessUDFS(BaseModel):
    lot_nr_beads_library_prep: str = Field(..., alias="Lot nr: Beads")
    lot_nr_etoh_library_prep: str = Field(..., alias="Lot nr: EtOH")
    lot_nr_h2o_library_prep: str = Field(..., alias="Lot nr: H2O")


class PostPCRBeadPurificationArtifactUDF(BaseModel):
    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[int] = Field(None, alias="Size (bp)")
    finished_library_average_size: float = Field(..., alias="Average Size (bp)")


class PostPCRBeadPurificationFields(BaseStep):
    process_udfs: PostPCRBeadPurificationProcessUDFS
    artifact_udfs: PostPCRBeadPurificationArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_post_bead_pcr_purification(
    lims: Lims, sample_id: str, prep_id: str
) -> PostPCRBeadPurificationFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Post-PCR bead purification v1",
    )

    return PostPCRBeadPurificationFields(
        **analyte.base_fields(),
        process_udfs=PostPCRBeadPurificationProcessUDFS(**analyte.process_udfs()),
        artifact_udfs=PostPCRBeadPurificationArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="post_pcr_bead_purification",
        workflow="Microbial"
    )
