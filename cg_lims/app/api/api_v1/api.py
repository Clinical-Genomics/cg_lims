from fastapi import FastAPI

from cg_lims.app.api.api_v1.endpoints import sample


app = FastAPI()

app.include_router(sample.router, prefix="/api/v1/samples", tags=["sample"])
