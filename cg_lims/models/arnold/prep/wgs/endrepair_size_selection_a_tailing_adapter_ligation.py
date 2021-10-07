from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


class EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAProcessUDFS(BaseModel):
    lot_nr_truseq_library_preparation_kit: Optional[str] = Field(
        None, alias="Lot no: TruSeq DNA PCR-Free Sample Prep Kit"
    )
    lot_nr_index: str = Field(..., alias="Lot no: Adaptor Plate")
    lot_nr_beads: str = Field(..., alias="Lot no: SP Beads")
    lot_nr_lucigen_library_preparation_kit: Optional[str] = Field(
        None, alias="Lot no: Lucigen prep kit"
    )
    pcr_instrument_incubation: str = Field(..., alias="PCR machine")
    lot_nr_h2o_library_preparation: str = Field(..., alias="Lot no: Nuclease free water")
    lot_nr_resuspension_buffer_library_preparation: str = Field(
        ..., alias="Lot no: Resuspension buffer"
    )
    library_preparation_method: str = Field(..., alias="Method document")
    lot_nr_etoh_library_preparation: str = Field(..., alias="Ethanol lot")


class EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF(BaseModel):
    finished_library_concentration: Optional[float] = Field(None, alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")


class EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS(
    EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAProcessUDFS,
    EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF,
):
    library_prep_well_position: Optional[str] = Field(None, alias="well_position")
    library_prep_container_name: Optional[str] = Field(None, alias="container_name")
    library_prep_index_name: Optional[str] = Field(None, alias="index_name")

    class Config:
        allow_population_by_field_name = True


def get_end_repair_udfs(
    lims: Lims, sample_id: str
) -> EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAProcessUDFS,
        artifact_udf_model=EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF,
        process_type="End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)",
    )

    return EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS(
        **analyte.merge_analyte_fields(),
    )
