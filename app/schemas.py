from datetime import datetime

from pydantic import BaseModel, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl


class LinkOut(BaseModel):
    code: str
    short_url: str
    target_url: str
    created_at: datetime
    clicks: int
