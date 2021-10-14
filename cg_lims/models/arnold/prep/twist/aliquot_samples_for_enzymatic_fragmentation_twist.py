from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class AliquotSamplesForEnzymaticFragmentationProcessUdfs(BaseModel):
    performance_NA24143: Optional[str] = Field(None, alias="Batch no Prep Performance NA24143")
    GMCKsolid_HD827: Optional[str] = Field(None, alias="Batch no GMCKsolid-HD827")
    GMSlymphoid_HD829: Optional[str] = Field(None, alias="Batch no GMSlymphoid-HD829")
    GMSmyeloid_HD829: Optional[str] = Field(None, alias="Batch no GMSmyeloid-HD829")
    aliquot_samples_library_preparation_method_2: str = Field(..., alias="Method document 2")
    aliquot_samples_library_preparation_method_1: str = Field(..., alias="Method document 1")
    lot_nr_h2o_aliquot_samples_fragmentation: str = Field(..., alias="Nuclease free water")


class AliquotSamplesForEnzymaticFragmentationArtifactUdfs(BaseModel):
    amount_needed: Optional[float] = Field(None, alias="Amount needed (ng)")


class AliquotSamplesForEnzymaticFragmentationFields(BaseStep):
    process_udfs: AliquotSamplesForEnzymaticFragmentationProcessUdfs
    artifact_udfs: AliquotSamplesForEnzymaticFragmentationArtifactUdfs

    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_enzymatic_fragmentation(
    lims: Lims, sample_id: str, prep_id: str
) -> AliquotSamplesForEnzymaticFragmentationFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Aliquot samples for enzymatic fragmentation TWIST v2",
    )

    return AliquotSamplesForEnzymaticFragmentationFields(
        **analyte.base_fields(),
        process_udfs=AliquotSamplesForEnzymaticFragmentationProcessUdfs(**analyte.process_udfs()),
        artifact_udfs=AliquotSamplesForEnzymaticFragmentationArtifactUdfs(
            **analyte.artifact_udfs()
        ),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="aliquot_samples_for_enzymatic_fragmentation",
        workflow="TWIST",
    )
