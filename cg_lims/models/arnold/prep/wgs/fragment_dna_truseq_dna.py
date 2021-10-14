from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class FragmentDNATruSeqDNAProcessUDFS(BaseModel):
    lot_nr_covaris_tube: str = Field(..., alias="Lot no: Covaris tube")
    fragmentation_method: str = Field(..., alias="Method Document 1")
    covaris_protocol: str = Field(..., alias="Protocol")
    lot_nr_resuspension_buffer_fragmentation: str = Field(..., alias="Lot no: Resuspension Buffer")


class FragmentDNATruSeqDNAFields(BaseStep):
    process_udfs: FragmentDNATruSeqDNAProcessUDFS

    class Config:
        allow_population_by_field_name = True


def get_fragemnt_dna_truseq(lims: Lims, sample_id: str, prep_id: str) -> FragmentDNATruSeqDNAFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Fragment DNA (TruSeq DNA)",
    )

    return FragmentDNATruSeqDNAFields(
        **analyte.base_fields(),
        process_udfs=FragmentDNATruSeqDNAProcessUDFS(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="fragment_dna",
        workflow="WGS",
    )
