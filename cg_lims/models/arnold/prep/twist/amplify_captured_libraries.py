from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class ProcessUDFs(BaseModel):
    amplify_captured_library_method: Optional[str] = Field(None, alias="Method Document")
    lot_nr_xgen_primer_amplify_captured_library: Optional[str] = Field(
        None, alias="xGen Library Amp primer"
    )
    lot_nr_amplification_kit_amplify_captured_library: Optional[str] = Field(
        None, alias="Kapa HiFi HotStart ReadyMix"
    )


class ArtifactUDFs(BaseModel):
    nr_pcr_cycles_amplify_captured_library: Optional[int] = Field(None, alias="Nr of PCR cycles")


class ArnoldStep(
    BaseStep,
):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_amplify_captured_library_udfs(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Amplify Captured Libraries TWIST v2",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="amplify_captured_library",
        workflow="TWIST",
    )
