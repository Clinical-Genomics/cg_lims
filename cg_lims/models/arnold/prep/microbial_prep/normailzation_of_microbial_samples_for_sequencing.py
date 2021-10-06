import logging
from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte

LOG = logging.getLogger(__name__)


class NormalizationOfSamplesForSequencingProcessUDFS(BaseModel):
    lot_nr_dilution_buffer_library_normalization: Optional[str] = Field(
        None, alias="Dilution buffer lot no"
    )
    normalized_library_concentration: Optional[float] = Field(
        None, alias="Final Concentration (nM)"
    )
    library_normalization_method: Optional[str] = Field(None, alias="Method document")


class NormalizationOfSamplesForSequencingUDFS(NormalizationOfSamplesForSequencingProcessUDFS):
    c_well_position: Optional[str] = Field(None, alias="well_position")
    c_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_normalization_of_samples_for_sequencing_udfs(
    lims: Lims, sample_id: str
) -> NormalizationOfSamplesForSequencingUDFS:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=NormalizationOfSamplesForSequencingProcessUDFS,
        process_type="CG002 - Normalization of microbial samples for sequencing",
    )

    return NormalizationOfSamplesForSequencingUDFS(
        **analyte.merge_analyte_fields(),
    )
