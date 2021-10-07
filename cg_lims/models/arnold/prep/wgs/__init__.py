from .fragment_dna_truseq_dna import (
    FragmentDNATruSeqDNAUDFS,
    FragmentDNATruSeqDNAProcessUDFS,
    get_fragemnt_dna_truseq_udfs,
)
from .aliquot_sampels_for_covaris import (
    AliquotSamplesforCovarisUDF,
    AliquotSamplesforCovarisArtifactUDF,
    get_aliquot_samples_for_covaris_udfs,
)
from .initial_qc import InitialQCwgsUDF, InitialQCwgsArtifactUDF, get_initial_qc_udfs
from .endrepair_size_selection_a_tailing_adapter_ligation import (
    EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS,
    EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAProcessUDFS,
    EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF,
    get_end_repair_udfs,
)
from cg_lims.models.arnold.prep.base_prep import Prep


class WGSPrep(
    Prep,
    FragmentDNATruSeqDNAUDFS,
    AliquotSamplesforCovarisUDF,
    InitialQCwgsUDF,
    EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS,
):
    workflow = "WGS"

    class Config:
        allow_population_by_field_name = True
