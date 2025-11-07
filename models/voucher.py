# models/voucher.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Voucher(BaseModel):
    name: str
    code: str
    value: str
    start_time: datetime
    end_time: datetime
    link: str
    description: Optional[str] = None
    source: str = "unknown"
    avatar: Optional[str] = None  # THÊM DÒNG NÀY