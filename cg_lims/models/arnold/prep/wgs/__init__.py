from typing import List

from genologics.lims import Lims

from .fragment_dna_truseq_dna import (
    FragmentDNATruSeqDNAFields,
    FragmentDNATruSeqDNAProcessUDFS,
    get_fragemnt_dna_truseq_udfs,
)
from .aliquot_sampels_for_covaris import (
    AliquotSamplesforCovarisFields,
    AliquotSamplesforCovarisArtifactUDF,
    get_aliquot_samples_for_covaris_udfs,
)
from .initial_qc import InitialQCwgsUDF, InitialQCwgsArtifactUDF, get_initial_qc_udfs
from .endrepair_size_selection_a_tailing_adapter_ligation import (
    EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeFields,
    EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeProcessUDFS,
    EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeArtifactUDF,
    get_end_repair_udfs,
)
from ..base_step import BaseStep


def build_wgs_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""

    prep_id = f"{sample_id}_{process_id}"
    return [
        get_fragemnt_dna_truseq_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_initial_qc_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_aliquot_samples_for_covaris_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_end_repair_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]
