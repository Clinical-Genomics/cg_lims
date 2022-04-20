from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ProcessUDFs(BaseModel):
    """Define Run Format and Calculate Volumes (Nova Seq)"""

    flowcell_type: Optional[str] = Field(None, alias="FlowCell Type")
    rsb_lot_nr: Optional[str] = Field(None, alias="RSB lot nr")
    final_loading_concentration: Optional[str] = Field(
        None, alias="Final Loading Concentration (pM)"
    )
    total_reads_requested: Optional[str] = Field(
        None, alias="Total nr of Reads Requested (sum of reads to sequence)"
    )
    method: Optional[str] = Field(None, alias="Method")
    protocol_type: Optional[str] = Field(None, alias="Protocol type")


class ArtifactUDFs(BaseModel):
    sequencing_molar_concentration: Optional[float] = Field(None, alias="Concentration (nM)")
    reads_to_sequence: Optional[float] = Field(None, alias="Reads to sequence (M)")
    adjusted_volume_per_sample: Optional[float] = Field(
        None, alias="Adjusted Per Sample Volume (ul)"
    )


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_define_run_format(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Define Run Format and Calculate Volumes (Nova Seq)",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="define_run_format",
        workflow="NovaSeq"
    )
