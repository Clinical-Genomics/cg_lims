from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ArtifactUDFs(BaseModel):
    library_size_pre_hyb: int = Field(..., alias="Size (bp)")
    library_concentration_pre_hyb: float = Field(..., alias="Concentration")
    adapter_ligation_master_mix: str = Field(..., alias="Ligation Master Mix")
    library_preparation_pcr_plate: str = Field(..., alias="PCR Plate")
    amount_of_sample_in_pool_ng: Optional[float] = Field(
        None, alias="Amount taken (ng)"
    )  # this value is set afterwards in the pooling step


class ProcessUDFs(BaseModel):
    hamilton_post_lab_library_preparation: Optional[str] = Field(alias="Hamilton (post-lab)")
    hamilton_pre_lab_library_preparation: Optional[str] = Field(alias="Hamilton (pre-lab)")
    method_document_library_preparation: str = Field(..., alias="Method document")
    library_preparation_kit: str = Field(..., alias="KAPA HyperPlus/Prep Kit")
    lot_nr_h2o_library_preparation_pre_lab: str = Field(..., alias="Nuclease-free water (pre-lab)")
    lot_nr_xgen_adapter: str = Field(..., alias="xGen Adapter")
    lot_nr_index: str = Field(..., alias="Indexing Primer")
    lot_nr_beads_library_preparation_pre_lab: str = Field(
        ..., alias="DNA purification beads (pre-lab)"
    )
    lot_nr_etoh_library_preparation_pre_lab: str = Field(..., alias="Ethanol (pre-lab)")
    pcr_instrument_end_repair_a_tail: str = Field(..., alias="PCR Machine: End Repair and A-tail")
    pcr_instrument_adapter_ligation: str = Field(..., alias="PCR Machine: Adapter ligation")
    pcr_instrument_amplification_plate1: Optional[str] = Field(
        None, alias="PCR Machine: Amplification Plate 1"
    )
    pcr_instrument_amplification_plate2: Optional[str] = Field(
        None, alias="PCR Machine: Amplification Plate 2"
    )
    pcr_instrument_amplification_plate3: Optional[str] = Field(
        None, alias="PCR Machine: Amplification Plate 3"
    )
    lot_nr_beads_library_preparation_post_lab: str = Field(
        ..., alias="DNA purification beads (post-lab)"
    )
    lot_nr_etoh_library_preparation_post_lab: str = Field(..., alias="Ethanol (post-lab)")
    lot_nr_h2o_library_preparation_post_lab: str = Field(
        ..., alias="Nuclease-free water (post-lab)"
    )


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_kapa_library_preparation_twist(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="KAPA Library Preparation TWIST v1",
    )
    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="kapa_library_preparation",
        workflow="TWIST",
    )
