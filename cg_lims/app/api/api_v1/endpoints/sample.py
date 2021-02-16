from fastapi import APIRouter, Depends
from cg_lims.app.build.sample import build_sample
from cg_lims.app.api.deps import get_lims
from cg_lims.app import schemas

from genologics.lims import Lims
from genologics.entities import Sample


router = APIRouter()


@router.get("/{sample_id}", response_model=schemas.Sample)
def get_sample(sample_id: str, lims: Lims = Depends(get_lims)):
    """get sample"""
    genologics_sample = Sample(lims, id=sample_id)
    sample = build_sample(genologics_sample)
    return sample
