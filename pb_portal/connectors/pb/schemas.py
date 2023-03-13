"""Pydantic's models."""
from pydantic import BaseModel


class PremTop(BaseModel):
    title: str
    url: str
    profit: int
    sales: int


class PlusTop(BaseModel):
    title: str
    url: str
    downloads: int


class PBStat(BaseModel):
    prem_by_profit: list[PremTop]
    prem_by_sales: list[PremTop]
    plus: list[PlusTop]
