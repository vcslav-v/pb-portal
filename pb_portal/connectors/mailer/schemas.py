"""Pydantic's models."""
from pydantic import BaseModel
from typing import Optional


class PbDigest(BaseModel):
    """Pydantic's model for the pb digest."""
    data: dict


class HTML(BaseModel):
    """Pydantic's model for the HTML."""
    result: str


class Bundle(BaseModel):
    """Pydantic's model for the bundle."""
    urls: list[str]
    num_products: int
    sum: int


class Video(BaseModel):
    """Pydantic's model for the video."""
    url: str
    title: str
    description: str
    duration: str
    lable: str
    button_text: str


class GalleryRow(BaseModel):
    """Pydantic's model for the gallery row."""
    left_img_num: int
    right_img_num: int


class PbFeatured(BaseModel):
    """Pydantic's model for the pb featured."""
    product_url: str
    first_try: bool = False
    html: str = ''
    preview_url: str = ''
    num_cover_img: int = 0
    label: str = 'New'
    exerpt: Optional[str]
    main_gallery_img_num: int = 1
    last_gallery_img_num: int = 2
    gallery_rows: list[GalleryRow] = []
    details: list[str] = []
    description: str = ''
    video: Optional[Video]
    bundle: Optional[Bundle]
    popular: list[str] = []


class PbFeaturedPage(BaseModel):
    """Pydantic's model for the pb featured page."""
    data: PbFeatured
    controls: str
