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
    pool_well_position: Optional[str] = Field(None, alias="well_position")
    pool_container_name: Optional[str] = Field(None, alias="container_name")
    pool_nr_samples: Optional[int] = Field(None, alias="nr_samples")

    class Config:
        allow_population_by_field_name = True


def get_pooling_and_cleanup_udfs(lims: Lims, sample_id: str) -> PoolingAndCleanUpCovUDF:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=PoolingAndCleanUpCovProcessUDFS,
        artifact_udf_model=PoolingAndCleanUpCovArtifactUDF,
        process_type="Pooling and Clean-up (Cov) v1",
    )

    return PoolingAndCleanUpCovUDF(
        **analyte.merge_analyte_fields(),
    )
