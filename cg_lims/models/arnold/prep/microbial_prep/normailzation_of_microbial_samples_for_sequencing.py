import logging
from typing import Optional
from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.objects import BaseAnalyte

LOG = logging.getLogger(__name__)


class ProcessUDFS(BaseModel):
    lot_nr_dilution_buffer_library_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )
    normalized_library_concentration: Optional[float] = Field(
        None, alias="Final Concentration (nM)"
    )
    library_normalization_method: Optional[str] = Field(None, alias="Method document")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFS

    class Config:
        allow_population_by_field_name = True


def get_normalization_of_samples(lims: Lims, sample_id: str, prep_id: str) -> Optional[ArnoldStep]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Normalization of microbial samples for sequencing",
        optional_step=True,
    )
    if not analyte.artifact:
        return None

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFS(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="normalization_for_sequencing",
        workflow="Microbial"
    )
