from pydantic import BaseModel


class Preview(BaseModel):
    id: int
    thumb_url: str
    filename: str


class UploadForm(BaseModel):
    session_id: str
    title: str = ''
    schedule_date: str = ''
    category_id: str = ''
    product_type: str = ''
    commercial_price: str = ''
    extended_price: str = ''
    product_name: str = ''
    formats: list[str] = []
    exerpt: str = ''
    desc: str = ''
    tags: str = ''
    previews: list[Preview] = []
