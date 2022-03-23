from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte

from cg_lims.models.arnold.prep.base_step import BaseStep


class ProcessUDFs(BaseModel):
    pooling_method: Optional[str] = Field(None, alias="Method document (pooling)")
    clean_up_method: Optional[str] = Field(None, alias="Method document (Clean-up)")
    lot_nr_beads_clean_up: Optional[str] = Field(None, alias="Purification beads")
    lot_nr_etoh_clean_up: Optional[str] = Field(None, alias="Ethanol")
    lot_nr_h2o_clean_up: Optional[str] = Field(None, alias="Nuclease-free water")
    lot_nr_resuspension_buffer_clean_up: Optional[str] = Field(None, alias="Resuspension buffer")


class ArtifactUDFs(BaseModel):
    finished_library_concentration: Optional[float] = Field(None, alias="Concentration")
    finished_library_concentration_nm: Optional[float] = Field(None, alias="Concentration (nM)")
    finished_library_size: Optional[int] = Field(None, alias="Size (bp)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_pooling_and_cleanup(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Pooling and Clean-up (Cov) v1",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="pooling_and_cleanup",
        workflow="sars_cov_2"
    )
