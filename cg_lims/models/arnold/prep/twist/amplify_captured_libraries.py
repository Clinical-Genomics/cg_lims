from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class AmplifycapturedLibrariestwistProcessUDFs(BaseModel):
    amplify_captured_library_method: str = Field(..., alias="Method Document")
    lot_nr_xgen_primer_amplify_captured_library: str = Field(..., alias="xGen Library Amp primer")
    lot_nr_amplification_kit_amplify_captured_library: str = Field(
        ..., alias="Kapa HiFi HotStart ReadyMix"
    )
    nr_pcr_cycles_amplify_captured_library: int = Field(..., alias="Nr of PCR cycles")


class AmplifycapturedLibrariestwistFields(
    BaseStep,
):
    process_udfs: AmplifycapturedLibrariestwistProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_amplify_captured_library_udfs(
    lims: Lims, sample_id: str, prep_id: str
) -> AmplifycapturedLibrariestwistFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Amplify Captured Libraries TWIST v2",
    )

    return AmplifycapturedLibrariestwistFields(
        **analyte.base_fields(),
        process_udfs=AmplifycapturedLibrariestwistProcessUDFs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="amplify_captured_library",
        workflow="TWIST",
    )
