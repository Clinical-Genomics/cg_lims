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
from cg_lims.models.arnold.prep.base_prep import Prep


class WGSPrep(Prep):
    fragemnt_dna_truseq: FragmentDNATruSeqDNAFields
    aliquot_samples_for_covaris: AliquotSamplesforCovarisFields
    initial_qc: InitialQCwgsUDF
    end_repair_size_selection_a_tailing: EndRepairSizeSelectionATailingAndAdapterligationTruSeqPCRFreeFields
    workflow = "WGS"

    class Config:
        allow_population_by_field_name = True
