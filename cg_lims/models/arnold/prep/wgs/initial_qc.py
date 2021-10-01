from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


class InitialQCwgsArtifactUDF(BaseModel):
    sample_concentration: float = Field(..., alias="Concentration")
    sample_amount: float = Field(..., alias="Amount (ng)")


class InitialQCwgsUDF(InitialQCwgsArtifactUDF):
    class Config:
        allow_population_by_field_name = True


def get_initial_qc_udfs(lims: Lims, sample_id: str) -> InitialQCwgsUDF:
    initial_qc = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=InitialQCwgsArtifactUDF,
        process_type="Pooling and Clean-up (Cov) v1",
    )

    return InitialQCwgsUDF(**initial_qc.merge_process_and_artifact_udfs())
