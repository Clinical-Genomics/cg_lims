from typing import List

from genologics.lims import Lims

from .define_run_format import get_define_run_format
from .standard_make_pool_and_denature import get_standard_make_pool_and_denature
from .standard_prepare_for_sequencing import get_standard_prepare_for_sequencing
from .xp_denature_and_examp import get_xp_denature_and_examp
from .xp_load_to_flowcell import get_xp_load_to_flowcell
from .bcl_conversion_and_demultiplexing import get_bcl_conversion_and_demultiplexing
from cg_lims.models.arnold.base_step import BaseStep


def build_novaseq_step_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a Step Documents for a NovaSeq sequencing run."""

    prep_id = f"{sample_id}_{process_id}"
    step_documents = [
        get_define_run_format(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_standard_make_pool_and_denature(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_standard_prepare_for_sequencing(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_xp_denature_and_examp(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_xp_load_to_flowcell(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_bcl_conversion_and_demultiplexing(
            sample_id=sample_id, lims=lims, prep_id=prep_id, process_id=process_id
        ),
    ]
    return [document for document in step_documents if document is not None]
