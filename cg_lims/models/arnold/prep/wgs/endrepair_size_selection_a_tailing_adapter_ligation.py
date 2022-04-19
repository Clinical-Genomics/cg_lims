from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.base_step import BaseStep


class ProcessUDFs(BaseModel):
    lot_nr_truseq_library_preparation_kit: Optional[str] = Field(
        None, alias="Lot no: TruSeq DNA PCR-Free Sample Prep Kit"
    )
    lot_nr_index: Optional[str] = Field(None, alias="Lot no: Adaptor Plate")
    lot_nr_beads: Optional[str] = Field(None, alias="Lot no: SP Beads")
    lot_nr_lucigen_library_preparation_kit: Optional[str] = Field(
        None, alias="Lot no: Lucigen prep kit"
    )
    pcr_instrument_incubation: Optional[str] = Field(None, alias="PCR machine")
    lot_nr_h2o_library_preparation: Optional[str] = Field(None, alias="Lot no: Nuclease free water")
    lot_nr_resuspension_buffer_library_preparation: Optional[str] = Field(
        None, alias="Lot no: Resuspension buffer"
    )
    methods: Optional[str] = Field(None, alias="Methods")
    atlas_version: Optional[str] = Field(None, alias="Atlas Version")
    lot_nr_etoh_library_preparation: Optional[str] = Field(None, alias="Ethanol lot")


class ArtifactUDFs(BaseModel):
    finished_library_concentration: Optional[float] = Field(None, alias="Concentration")
    finished_library_concentration_nm: Optional[float] = Field(None, alias="Concentration (nM)")
    finished_library_size: Optional[int] = Field(None, alias="Size (bp)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_end_repair(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="end_repair",
        workflow="WGS",
    )
