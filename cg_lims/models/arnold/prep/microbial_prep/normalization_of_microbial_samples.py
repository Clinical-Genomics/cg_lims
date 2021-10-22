from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class NormalizationProcessUDFS(BaseModel):
    sample_normalization_method: Optional[str] = Field(None, alias="Method document")
    normalized_sample_concentration: Optional[float] = Field(
        None, alias="Final Concentration (ng/ul)"
    )
    lot_nr_dilution_buffer_sample_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )


class NormalizationFields(BaseStep):
    process_udfs: NormalizationProcessUDFS

    class Config:
        allow_population_by_field_name = True


def get_normalization_of_mictobial_samples(
    lims: Lims, sample_id: str, prep_id: str
) -> NormalizationFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Normalization of microbial samples",
    )

    return NormalizationFields(
        **analyte.base_fields(),
        process_udfs=NormalizationProcessUDFS(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="normalization",
        workflow="Microbial"
    )
