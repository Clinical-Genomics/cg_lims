from pydantic import BaseModel
import datetime as dt
from typing import Optional


class Sample(BaseModel):
    ""

    id: str
    name: str
    project: str
    comment: Optional[str]
    processing_time: Optional[dt.datetime] = None
    received_date: Optional[dt.date] = None
    prepared_date: Optional[dt.date] = None
    sequenced_date: Optional[dt.date] = None
    delivery_date: Optional[dt.date] = None
