from pydantic import BaseModel
import datetime as dt
from typing import Optional


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
