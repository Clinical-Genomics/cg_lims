from pydantic import BaseModel
import datetime as dt
from typing import Optional

from cg_lims.app.schemas.workflows.twist_3 import Twist3


class Sample(BaseModel):
    id: str
    name: str
    project: str
    comment: Optional[str]
    processing_time: Optional[dt.datetime]
    received_date: Optional[dt.date]
    prepared_date: Optional[dt.date]
    sequenced_date: Optional[dt.date]
    delivery_date: Optional[dt.date]
    twist: Optional[Twist3]
