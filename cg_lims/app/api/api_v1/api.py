from fastapi import APIRouter, FastAPI

from cg_lims.app.api.api_v1.endpoints import sample

app = FastAPI()

# api_router = APIRouter()
app.include_router(sample.router, prefix="/api/v1/samples", tags=["sample"])
