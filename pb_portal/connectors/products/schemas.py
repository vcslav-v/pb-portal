"""Pydantic's models."""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime


class ProductInPage(BaseModel):
    ident: int
    title: str
    designer_name: str
    category: str
    trello_link: str
    start_date: date
    end_production_date: Optional[date]
    is_big: bool = False
    days_in_work: int = 0

    @validator('days_in_work', pre=True, always=True)
    def calc_days_in_work(cls, v, values):
        if values.get('start_date') and values.get('end_production_date'):
            return (values.get('end_production_date') - values.get('start_date')).days
        return 0




class Designer(BaseModel):
    ident: int
    name: str


class ProductPage(BaseModel):
    products: list[ProductInPage] = []
    page: int = 1
    number_pages: int = 1
    number_products: int = 0
    number_big_products: int = 0


class Category(BaseModel):
    ident: int
    name: str


class ProductPageData(BaseModel):
    designers: list[Designer] = []
    categories: list[Category] = []


class FilterPage(BaseModel):
    page: int = 1
    designer_id: Optional[int]
    category_id: Optional[int]
    end_design_date_start: Optional[date]
    end_design_date_end: Optional[date]


class Features(BaseModel):
    title: str
    value: str


class MetaTags(BaseModel):
    title: str
    description: str
    key_words: list[str]


class UploadProductPageInfo(BaseModel):
    categories: list[str] = []
    formats: list[str] = []
    compatibilities: list[str] = []
    items_in_col: int = 5
    tags: dict


class UploadProduct(BaseModel):
    prefix: str
    product_file_name: str
    title: str
    slug: str
    excerpt: str
    size: str
    description: str
    date_upload: datetime
    schedule_date: Optional[datetime]
    guest_author: Optional[str]
    guest_author_link: Optional[str]
    categories: list[str] = []
    formats: list[str] = []
    tags: list[str] = []


class UploadFreebie(UploadProduct):
    download_by_email: bool = False


class UploadPlus(UploadProduct):
    pass


class UploadPrem(UploadProduct):
    standart_price: Optional[int]
    extended_price: Optional[int]
    sale_standart_price: Optional[int]
    sale_extended_price: Optional[int]
    compatibilities: list[str] = []


class ScheduleUpdate(BaseModel):
    date_time: datetime


class ProductsSchedule(ScheduleUpdate):
    ident: int
    name: str
    edit_link: str


class PageProductsSchedule(BaseModel):
    page: list[ProductsSchedule] = []
