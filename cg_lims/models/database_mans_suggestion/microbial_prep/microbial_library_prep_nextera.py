import logging

from genologics.entities import Artifact
from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.get.artifacts import get_latest_artifact

LOG = logging.getLogger(__name__)


class MicrobialLibraryPrepNexteraProcessUDFS(BaseModel):
    lot_nr_tagmentation_buffer: str = Field(..., alias="Lot nr: Tagmentation buffer (TD-buffer)")
    lot_nr_tagmentation_enzyme: str = Field(..., alias="Lot nr: Tagmentation enzyme (TDE1)")
    lot_nr_index: str = Field(..., alias="Lot nr: Index")
    lot_nr_pcr_mix: str = Field(..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)")
    pcr_instrument_incubation: str = Field(..., alias="PCR instrument incubation")
    pcr_instrument_amplification: str = Field(..., alias="PCR instrument amplification")
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")


class MicrobialLibraryPrepUDFS(MicrobialLibraryPrepNexteraProcessUDFS):
    class Config:
        allow_population_by_field_name = True


def get_microbial_library_prep_nextera_process_udfs(
    artifact: Artifact,
) -> MicrobialLibraryPrepNexteraProcessUDFS:
    process_udfs = dict(artifact.parent_process.udf.items())
    return MicrobialLibraryPrepNexteraProcessUDFS(**process_udfs)


def get_microbial_library_prep_nextera_udfs(lims: Lims, sample_id: str) -> MicrobialLibraryPrepUDFS:
    process_type = "CG002 - Microbial Library Prep (Nextera)"

    artifact: Artifact = get_latest_artifact(
        lims=lims, sample_id=sample_id, process_type=[process_type]
    )

    buffer_exchange_process_udfs: MicrobialLibraryPrepNexteraProcessUDFS = (
        get_microbial_library_prep_nextera_process_udfs(artifact=artifact)
    )

    # Merging artifact udfs and process udfs
    buffer_exchange_udfs = buffer_exchange_process_udfs.dict(exclude_none=True)
    buffer_exchange_udfs.update(buffer_exchange_artifact_udfs.dict(exclude_none=True))
    return MicrobialLibraryPrepUDFS(**buffer_exchange_udfs)
