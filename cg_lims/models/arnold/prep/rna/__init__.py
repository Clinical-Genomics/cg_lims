from typing import List

from genologics.lims import Lims

from .a_tailing_and_adapter_ligation import get_a_tailning_and_adapter_ligation
from .aliquot_samples_for_fragmentation import get_aliquot_samples_for_enzymatic_fragmentation
from .reception_control import get_sample_artifact_fields
from .normalization_of_samples_for_sequencing import get_normalization_of_samples
from cg_lims.models.arnold.base_step import BaseStep


def build_rna_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a RNA Prep."""
    prep_id = f"{sample_id}_{process_id}"
    step_documents = [
        get_normalization_of_samples(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_a_tailning_and_adapter_ligation(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_sample_artifact_fields(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_aliquot_samples_for_enzymatic_fragmentation(
            sample_id=sample_id, lims=lims, prep_id=prep_id
        ),
    ]
    return [document for document in step_documents if document is not None]
