from fastapi import APIRouter
from cg_lims.app.build.sample import build_sample

from cg_lims.app import schemas

router = APIRouter()


@router.get("/{sample_id}", response_model=schemas.Sample)
def get_sample(sample_id: str):
    """get sample"""

    sample = build_sample(sample_id)
    return sample
