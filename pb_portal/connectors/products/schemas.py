"""Pydantic's models."""
from pydantic import BaseModel
from typing import Optional
from datetime import date


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


class Designer(BaseModel):
    ident: int
    name: str


class ProductPage(BaseModel):
    products: list[ProductInPage] = []
    page: int = 1
    number_pages: int = 1


class ProductPageData(BaseModel):
    designers: list[Designer] = []


class FilterPage(BaseModel):
    page: int = 1
    designer_id: Optional[int]
    end_date_start: Optional[date]
    end_date_end: Optional[date]
