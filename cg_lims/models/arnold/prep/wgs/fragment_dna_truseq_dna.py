from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


class FragmentDNATruSeqDNAProcessUDFS(BaseModel):
    lot_nr_covaris_tube: str = Field(..., alias="Lot no: Covaris tube")
    fragmentation_method: str = Field(..., alias="Method Document 1")
    covaris_protocol: str = Field(..., alias="Protocol")
    lot_nr_resuspension_buffer_fragmentation: str = Field(..., alias="Lot no: Resuspension Buffer")


class FragmentDNATruSeqDNAUDFS(FragmentDNATruSeqDNAProcessUDFS):
    fragmentation_well_position: Optional[str] = Field(None, alias="well_position")
    fragmentation_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_fragemnt_dna_truseq_udfs(lims: Lims, sample_id: str) -> FragmentDNATruSeqDNAUDFS:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=FragmentDNATruSeqDNAProcessUDFS,
        process_type="Fragment DNA (TruSeq DNA)",
    )

    return FragmentDNATruSeqDNAUDFS(
        **analyte.merge_analyte_fields(),
    )
