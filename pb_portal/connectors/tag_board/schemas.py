"""Pydantic's models."""
from pydantic import BaseModel


class Item(BaseModel):
    """Item model."""
    batch: int
    title: str
    tags: list[str]


class SearchResult(BaseModel):
    """Search result model."""
    items: list[Item]
    tags_stat: list[tuple[str, int]]
