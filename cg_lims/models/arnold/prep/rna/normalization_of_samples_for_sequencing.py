import logging
from typing import Optional
from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte

LOG = logging.getLogger(__name__)


class ProcessUDFs(BaseModel):
    """Normalization of RNA samples for sequencing v1"""

    dilution_lot_nr: Optional[str] = Field(None, alias="Dilution buffer lot no")


class ArtifactUDFs(BaseModel):
    concentration: Optional[float] = Field(None, alias="Concentration")
    size: Optional[int] = Field(None, alias="Size (bp)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_normalization_of_samples(lims: Lims, sample_id: str, prep_id: str) -> Optional[ArnoldStep]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Normalization of RNA samples for sequencing v1",
        optional_step=True,
    )
    if not analyte.artifact:
        return None

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="normalization_for_sequencing",
        workflow="RNA"
    )
