"""Pydantic's models."""
from pydantic import BaseModel


class PbDigest(BaseModel):
    """Pydantic's model for the pb digest."""
    data: dict


class HTML(BaseModel):
    """Pydantic's model for the HTML."""
    result: str
