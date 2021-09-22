import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.database.base_prep import BasePrep

LOG = logging.getLogger(__name__)


class PostPCRBeadPurification(BasePrep):
    def __init__(self, lims: Lims, sample_id: str):
        super().__init__(lims=lims, sample_id=sample_id)
        self.process_type = "Post-PCR bead purification v1"
        self.process_udf_model = PostPCRBeadPurificationProcessUDFS
        self.artifact_udf_model = PostPCRBeadPurificationArtifactUDF
        self.artifact = self.set_artifact()


class PostPCRBeadPurificationProcessUDFS(BaseModel):
    lot_nr_beads_library_prep: str = Field(..., alias="Lot nr: Beads")
    lot_nr_etoh_library_prep: str = Field(..., alias="Lot nr: EtOH")
    lot_nr_h2o_library_prep: str = Field(..., alias="Lot nr: H2O")


class PostPCRBeadPurificationArtifactUDF(BaseModel):
    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")
    finished_library_average_size: float = Field(..., alias="Average Size (bp)")
