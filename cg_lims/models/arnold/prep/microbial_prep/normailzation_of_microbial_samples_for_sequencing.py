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
    class Config:
        allow_population_by_field_name = True


def get_normalization_of_samples_for_sequencing_udfs(
    lims: Lims, sample_id: str
) -> NormalizationOfSamplesForSequencingUDFS:
    normalization_of_samples_for_sequencing = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=NormalizationOfSamplesForSequencingProcessUDFS,
        process_type="CG002 - Normalization of microbial samples for sequencing",
    )

    return NormalizationOfSamplesForSequencingUDFS(
        **normalization_of_samples_for_sequencing.merge_process_and_artifact_udfs()
    )
