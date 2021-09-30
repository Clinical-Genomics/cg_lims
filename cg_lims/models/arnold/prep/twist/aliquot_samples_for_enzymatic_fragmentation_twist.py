from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte


class AliquotSamplesForEnzymaticFragmentationProcessUdfs(BaseModel):
    performance_NA24143: Optional[str] = Field(None, alias="Batch no Prep Performance NA24143")
    GMCKsolid_HD827: Optional[str] = Field(None, alias="Batch no GMCKsolid-HD827")
    GMSlymphoid_HD829: Optional[str] = Field(None, alias="Batch no GMSlymphoid-HD829")
    GMSmyeloid_HD829: Optional[str] = Field(None, alias="Batch no GMSmyeloid-HD829")


class AliquotSamplesForEnzymaticFragmentationArtifactUdfs(BaseModel):
    amount_needed: Optional[str] = Field(None, alias="Amount needed (ng)")


class AliquotSamplesForEnzymaticFragmentationUdfs(
    AliquotSamplesForEnzymaticFragmentationArtifactUdfs,
    AliquotSamplesForEnzymaticFragmentationProcessUdfs,
):
    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_enzymatic_fragmentation_udfs(
    lims: Lims, sample_id: str
) -> AliquotSamplesForEnzymaticFragmentationUdfs:
    aliquot_samples_for_enzymatic_fragmentation = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=AliquotSamplesForEnzymaticFragmentationProcessUdfs,
        artifact_udf_model=AliquotSamplesForEnzymaticFragmentationArtifactUdfs,
        process_type="Aliquot samples for enzymatic fragmentation TWIST v2",
    )

    return AliquotSamplesForEnzymaticFragmentationUdfs(
        **aliquot_samples_for_enzymatic_fragmentation.merge_process_and_artifact_udfs()
    )
