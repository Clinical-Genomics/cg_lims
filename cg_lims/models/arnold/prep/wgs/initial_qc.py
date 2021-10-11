from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte

from cg_lims.models.arnold.prep.base_step import BaseStep


class InitialQCwgsArtifactUDF(BaseModel):
    sample_concentration: float = Field(..., alias="Concentration")
    sample_amount: float = Field(..., alias="Amount (ng)")


class InitialQCwgsUDF(BaseStep):
    artifact_udfs: InitialQCwgsArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_initial_qc_udfs(lims: Lims, sample_id: str, prep_id: str) -> InitialQCwgsUDF:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
    )

    return InitialQCwgsUDF(
        **analyte.base_fields(),
        artifact_udfs=InitialQCwgsArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="initial_qc",
        workflow="WGS"
    )
