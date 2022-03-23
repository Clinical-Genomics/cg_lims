from typing import List

from genologics.lims import Lims

from .define_run_format import get_define_run_format

from cg_lims.models.arnold.base_step import BaseStep


def build_novaseq_step_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a Step Documents for a NovaSeq sequencing run."""

    prep_id = f"{sample_id}_{process_id}"
    step_documents = [
        get_define_run_format(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]
    return [document for document in step_documents if document is not None]
