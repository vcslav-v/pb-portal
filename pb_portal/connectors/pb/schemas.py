"""Pydantic's models."""
from pydantic import BaseModel
from typing import Optional


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


class ProductInfo(BaseModel):
    pr_type: str
    url: str
    title: str
    main_img_url: str
    gallery_urls: list[str]
    exerpt: str
    regular_price: Optional[int]
    sale_regular_price: Optional[int]


class Affiliate(BaseModel):
    ident: int
    name: str
    url: str
    ref_num: int
    profit: int
    to_pay: int


class AffiliateInfo(BaseModel):
    affilates: list[Affiliate] = []
    aff_num: int = 0
    ref_num: int = 0
    profit_sum: int = 0
    to_pay_sum: int = 0
