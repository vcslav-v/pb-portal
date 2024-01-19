"""Pydantic's models."""
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional
from datetime import date, datetime
from pb_admin import schemas as pb_schemas


class ProductInPage(BaseModel):
    ident: int
    title: str
    designer_name: str
    category: str
    trello_link: str
    start_date: date
    end_production_date: Optional[date] = None
    is_big: bool = False
    adobe_count: int = 0
    days_in_work: int = 0

    @field_validator('days_in_work', mode='wrap')
    @classmethod
    def calc_days_in_work(cls, v, info: ValidationInfo):
        values = info.data
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
    total_adobe_count: int = 0


class Category(BaseModel):
    ident: int
    name: str


class ProductPageData(BaseModel):
    designers: list[Designer] = []
    categories: list[Category] = []


class FilterPage(BaseModel):
    page: int = 1
    designer_id: Optional[int] = None
    category_id: Optional[int] = None
    end_design_date_start: Optional[date] = None
    end_design_date_end: Optional[date] = None


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
    schedule_date: Optional[datetime] = None
    guest_author: Optional[str] = None
    guest_author_link: Optional[str] = None
    categories: list[str] = []
    formats: list[str] = []
    tags: list[str] = []


class UploadFreebie(UploadProduct):
    download_by_email: bool = False


class UploadPlus(UploadProduct):
    pass


class UploadPrem(UploadProduct):
    standart_price: Optional[int] = None
    extended_price: Optional[int] = None
    sale_standart_price: Optional[int] = None
    sale_extended_price: Optional[int] = None
    compatibilities: list[str] = []


class ScheduleUpdate(BaseModel):
    date_time: datetime


class ProductsSchedule(ScheduleUpdate):
    ident: int
    name: str
    edit_link: str


class PageProductsSchedule(BaseModel):
    page: list[ProductsSchedule] = []


class BulkTag(BaseModel):
    tag: str
    products: list[pb_schemas.Product]
