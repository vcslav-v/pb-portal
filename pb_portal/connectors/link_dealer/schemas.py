"""Pydantic's models."""
from pydantic import BaseModel


class utm(BaseModel):
    desc: str
    link: str
    short_link: str


class utms(BaseModel):
    utms: list[utm] = []
