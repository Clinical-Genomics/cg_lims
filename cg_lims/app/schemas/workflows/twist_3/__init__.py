from typing import Optional

from pydantic import BaseModel
from .protocols import (
    PreProcessingTWISTv2,
    InitialQCTWISTv3,
    LibraryPrepTWISTv2,
    LibraryValidationQCTWISTv2,
    TargetEnrichmentTWISTv2,
)


class Twist3(BaseModel):
    pre_processing: Optional[PreProcessingTWISTv2]
    initial_qc: Optional[InitialQCTWISTv3]
    library_prep: Optional[LibraryPrepTWISTv2]
    first_library_validation: Optional[LibraryValidationQCTWISTv2]
    target_enrichment: Optional[TargetEnrichmentTWISTv2]
    second_library_validation: Optional[LibraryValidationQCTWISTv2]
