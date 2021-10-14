from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte

from cg_lims.models.arnold.prep.base_step import BaseStep


class PoolingAndCleanUpCovProcessUDFS(BaseModel):
    pooling_method: str = Field(..., alias="Method document (pooling)")
    clean_up_method: str = Field(..., alias="Method document (Clean-up)")
    lot_nr_beads_clean_up: str = Field(..., alias="Purification beads")
    lot_nr_etoh_clean_up: str = Field(..., alias="Ethanol")
    lot_nr_h2o_clean_up: str = Field(..., alias="Nuclease-free water")
    lot_nr_resuspension_buffer_clean_up: str = Field(..., alias="Resuspension buffer")


class PoolingAndCleanUpCovArtifactUDF(BaseModel):
    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[int] = Field(None, alias="Size (bp)")


class PoolingAndCleanUpCovFields(BaseStep):
    process_udfs: PoolingAndCleanUpCovProcessUDFS
    artifact_udfs: PoolingAndCleanUpCovArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_pooling_and_cleanup(lims: Lims, sample_id: str, prep_id: str) -> PoolingAndCleanUpCovFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Pooling and Clean-up (Cov) v1",
    )

    return PoolingAndCleanUpCovFields(
        **analyte.base_fields(),
        process_udfs=PoolingAndCleanUpCovProcessUDFS(**analyte.process_udfs()),
        artifact_udfs=PoolingAndCleanUpCovArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="pooling_and_cleanup",
        workflow="sars_cov_2"
    )
