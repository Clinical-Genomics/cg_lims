from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


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
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")


class PoolingAndCleanUpCovUDF(PoolingAndCleanUpCovProcessUDFS, PoolingAndCleanUpCovArtifactUDF):
    class Config:
        allow_population_by_field_name = True


def get_pooling_and_cleanup_udfs(lims: Lims, sample_id: str) -> PoolingAndCleanUpCovUDF:
    pooling_and_cleanup = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=PoolingAndCleanUpCovProcessUDFS,
        artifact_udf_model=PoolingAndCleanUpCovArtifactUDF,
        process_type="Pooling and Clean-up (Cov) v1",
    )

    return PoolingAndCleanUpCovUDF(**pooling_and_cleanup.merge_process_and_artifact_udfs())
