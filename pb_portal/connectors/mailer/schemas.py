"""Pydantic's models."""
from pydantic import BaseModel
from typing import Optional


class PbDigest(BaseModel):
    """Pydantic's model for the pb digest."""
    data: dict
    campaign_name: str | None = None


class HTML(BaseModel):
    """Pydantic's model for the HTML."""
    result: str


class Bundle(BaseModel):
    """Pydantic's model for the bundle."""
    urls: list[str]
    num_products: int
    sum: str


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
    exerpt: Optional[str] = None
    main_gallery_img_num: int = 1
    last_gallery_img_num: int = 2
    gallery_rows: list[GalleryRow] = []
    details: list[str] = []
    description: str = ''
    video: Optional[Video] = None
    bundle: Optional[Bundle] = None
    popular: list[str] = []
    campaign_name: str | None = None
    beefree: str | None = None


class PbFeaturedPage(BaseModel):
    """Pydantic's model for the pb featured page."""
    data: PbFeatured
    controls: str


class HTML_with_UTM(BaseModel):
    html: str
    chanel: str = 'email_custom'
    campaign_project: str | int = 'pb'
    campaning_dop: str | None = None