from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


class NormalizationOfMicrobialSamplesProcessUDFS(BaseModel):
    sample_normalization_method: Optional[str] = Field(None, alias="Method document")
    normalized_sample_concentration: Optional[float] = Field(
        None, alias="Final Concentration (ng/ul)"
    )
    lot_nr_dilution_buffer_sample_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )


class NormalizationOfMicrobialSamplesUDFS(NormalizationOfMicrobialSamplesProcessUDFS):
    normalization_well_position: Optional[str] = Field(None, alias="well_position")
    normalization_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_normalization_of_mictobial_samples_udfs(
    lims: Lims, sample_id: str
) -> NormalizationOfMicrobialSamplesUDFS:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=NormalizationOfMicrobialSamplesProcessUDFS,
        process_type="CG002 - Normalization of microbial samples",
    )

    return NormalizationOfMicrobialSamplesUDFS(
        **analyte.merge_analyte_fields(),
    )
