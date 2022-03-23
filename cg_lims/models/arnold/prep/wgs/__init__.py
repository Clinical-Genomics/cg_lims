from typing import List

from genologics.lims import Lims

from .fragment_dna_truseq_dna import get_fragemnt_dna_truseq
from .aliquot_sampels_for_covaris import get_aliquot_samples_for_covaris
from .reception_control import get_sample_artifact_fields
from .endrepair_size_selection_a_tailing_adapter_ligation import get_end_repair
from ..base_step import BaseStep


def build_wgs_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""

    prep_id = f"{sample_id}_{process_id}"
    step_documents = [
        get_fragemnt_dna_truseq(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_sample_artifact_fields(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_aliquot_samples_for_covaris(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_end_repair(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]
    return [document for document in step_documents if document is not None]
