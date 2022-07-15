"""Pydantic's models."""
from __future__ import annotations
from pydantic import BaseModel
from datetime import date


class ContractInfo(BaseModel):
    ident: int
    selfemployed_name: str
    sevice_name: str
    amount: int
    contract_num: str
    contract_date: date
    is_check: bool
    is_signed: bool


class Page(BaseModel):
    contracts: list[ContractInfo]
