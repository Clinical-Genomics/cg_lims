from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.base_step import BaseStep


class ProcessUDFs(BaseModel):
    performance_NA24143: Optional[str] = Field(None, alias="Batch no Prep Performance NA24143")
    GMCKsolid_HD827: Optional[str] = Field(None, alias="Batch no GMCKsolid-HD827")
    GMSlymphoid_HD829: Optional[str] = Field(None, alias="Batch no GMSlymphoid-HD829")
    GMSmyeloid_HD829: Optional[str] = Field(None, alias="Batch no GMSmyeloid-HD829")
    GMSsolid_HD832: Optional[str] = Field(None, alias="Batch no GMSsolid-HD832")
    aliquot_samples_library_preparation_method_2: Optional[str] = Field(
        None, alias="Method document 2"
    )
    aliquot_samples_library_preparation_method_1: Optional[str] = Field(
        None, alias="Method document 1"
    )
    lot_nr_h2o_aliquot_samples_fragmentation: Optional[str] = Field(
        None, alias="Nuclease free water"
    )


class ArtifactUDFs(BaseModel):
    amount_needed: Optional[float] = Field(None, alias="Amount needed (ng)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_enzymatic_fragmentation(
    lims: Lims, sample_id: str, prep_id: str
) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Aliquot samples for enzymatic fragmentation TWIST v2",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="aliquot_samples_for_enzymatic_fragmentation",
        workflow="TWIST",
    )
