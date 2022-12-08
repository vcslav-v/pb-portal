"""Pydantic's models."""
from pydantic import BaseModel


class TextGPT(BaseModel):
    prompt: str
    tokens: int = 200
    quantity: int = 1
