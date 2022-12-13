"""Pydantic's models."""
from __future__ import annotations
from pydantic import BaseModel
from datetime import date
from typing import Optional


class ProductInPage(BaseModel):
    ident: str
    title: str
    short_description: str
    designer_name: str
    designer_id: int
    category: str
    category_id: int
    trello_link: str
    dropbox_link: str
    children: list['ProductInPage'] = []
    is_done: bool
    start_date: date
    end_date: Optional[date]


class ProductPage(BaseModel):
    products: list[ProductInPage] = []
