import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.objects import BaseAnalyte

LOG = logging.getLogger(__name__)


class ProcessUDFs(BaseModel):
    lot_nr_beads_library_prep: Optional[str] = Field(None, alias="Lot nr: Beads")
    lot_nr_etoh_library_prep: Optional[str] = Field(None, alias="Lot nr: EtOH")
    lot_nr_h2o_library_prep: Optional[str] = Field(None, alias="Lot nr: H2O")


class ArtifactUDFs(BaseModel):
    finished_library_concentration: Optional[float] = Field(None, alias="Concentration")
    finished_library_concentration_nm: Optional[float] = Field(None, alias="Concentration (nM)")
    finished_library_size: Optional[int] = Field(None, alias="Size (bp)")
    finished_library_average_size: Optional[float] = Field(None, alias="Average Size (bp)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_post_bead_pcr_purification(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Post-PCR bead purification v1",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="post_pcr_bead_purification",
        workflow="Microbial"
    )
