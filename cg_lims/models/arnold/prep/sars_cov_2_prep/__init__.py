from typing import List

from genologics.lims import Lims
from .library_preparation import get_library_prep_cov
from .pooling_and_cleanup import get_pooling_and_cleanup
from .reception_control import get_sample_artifact_fields
from ..base_step import BaseStep


def build_sars_cov_2_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""
    prep_id = f"{sample_id}_{process_id}"
    step_documents = [
        get_pooling_and_cleanup(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_library_prep_cov(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_sample_artifact_fields(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]
    return [document for document in step_documents if document is not None]
