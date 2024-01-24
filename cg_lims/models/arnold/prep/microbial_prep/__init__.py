from typing import List

from cg_lims.models.arnold.base_step import BaseStep
from genologics.lims import Lims

from .buffer_exchange import get_buffer_exchange
from .microbial_library_prep_nextera import get_library_prep_nextera
from .normailzation_of_microbial_samples_for_sequencing import get_normalization_of_samples
from .normalization_of_microbial_samples import get_normalization_of_mictobial_samples
from .post_pcr_bead_purification import get_post_bead_pcr_purification
from .reception_control import get_sample_artifact_fields


def build_microbial_step_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a Step Documents for a Microbial Prep."""

    prep_id = f"{sample_id}_{process_id}"
    step_documents = [
        get_sample_artifact_fields(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_library_prep_nextera(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_buffer_exchange(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_normalization_of_samples(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_normalization_of_mictobial_samples(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_post_bead_pcr_purification(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]
    return [document for document in step_documents if document is not None]
