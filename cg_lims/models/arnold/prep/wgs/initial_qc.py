from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte

## what is this? Initial sample???


class InitialQCwgsArtifactUDF(BaseModel):
    sample_concentration: float = Field(..., alias="Concentration")
    sample_amount: float = Field(..., alias="Amount (ng)")


class InitialQCwgsUDF(InitialQCwgsArtifactUDF):
    class Config:
        allow_population_by_field_name = True


def get_initial_qc_udfs(lims: Lims, sample_id: str) -> InitialQCwgsUDF:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=InitialQCwgsArtifactUDF,
    )

    return InitialQCwgsUDF(**analyte.merge_analyte_fields())
