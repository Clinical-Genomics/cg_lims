from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeProcessUDFS(BaseModel):
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


class EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeArtifactUDF(BaseModel):
    finished_library_concentration: Optional[float] = Field(None, alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[int] = Field(None, alias="Size (bp)")


class EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeFields(BaseStep):
    process_udfs: EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeProcessUDFS
    artifact_udfs: EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_end_repair(
    lims: Lims, sample_id: str, prep_id: str
) -> EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)",
    )

    return EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeFields(
        **analyte.base_fields(),
        process_udfs=EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeProcessUDFS(
            **analyte.process_udfs()
        ),
        artifact_udfs=EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeArtifactUDF(
            **analyte.artifact_udfs()
        ),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="end_repair",
        workflow="WGS",
    )
