from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte


class AmplifycapturedlibrariestwistProcessUDFs(BaseModel):
    amplify_captured_library_method: str = Field(..., alias="Method Document")
    lot_nr_xgen_primer_amplify_captured_library: str = Field(..., alias="xGen Library Amp primer")
    lot_nr_amplification_kit_amplify_captured_library: str = Field(
        ..., alias="Kapa HiFi HotStart ReadyMix"
    )
    nr_pcr_cycles_amplify_captured_library: str = Field(..., alias="Nr of PCR cycles")


class AmplifycapturedlibrariestwistUDFs(
    AmplifycapturedlibrariestwistProcessUDFs,
):
    amplify_captured_library__well_position: Optional[str] = Field(None, alias="well_position")
    amplify_captured_library_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_amplify_captured_library_udfs(
    lims: Lims, sample_id: str
) -> AmplifycapturedlibrariestwistUDFs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=AmplifycapturedlibrariestwistProcessUDFs,
        process_type="Amplify Captured Libraries TWIST v2",
    )

    return AmplifycapturedlibrariestwistUDFs(
        **analyte.merge_analyte_fields(),
    )
