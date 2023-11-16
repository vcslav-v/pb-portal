"""Pydantic's models."""
from __future__ import annotations
from pydantic import BaseModel
from datetime import date
from typing import Optional


class ContractInfo(BaseModel):
    ident: int
    selfemployed_name: str
    sevice_name: str
    amount: int
    contract_num: str
    contract_date: date
    is_check: bool
    is_signed: bool


class SelfEmployerInfo(BaseModel):
    ident: int
    fio_short: str


class ServiceInfo(BaseModel):
    ident: int
    name: str


class Page(BaseModel):
    contracts: list[ContractInfo]
    selfemployers: list[SelfEmployerInfo]
    serices: list[ServiceInfo]


class Contract(BaseModel):
    id_company: int = 1
    id_selfemployed: int
    id_sevice: int
    additional_service_desc: Optional[list[str]] = []
    ammount: int
    contract_date: Optional[date] = None
