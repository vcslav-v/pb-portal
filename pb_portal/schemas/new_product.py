from pydantic import BaseModel


class Preview(BaseModel):
    id: int
    thumb_url: str
    filename: str


class Errors(BaseModel):
    file_upload: bool = False
    formats: bool = False
    desc: bool = False
    previews: bool = False


class UploadForm(BaseModel):
    session_id: str
    title: str = ''
    schedule_date: str = ''
    creator_id: str = ''
    category_id: str = ''
    product_type: str = ''
    commercial_price: str = ''
    extended_price: str = ''
    product_name: str = ''
    formats: list[str] = []
    exerpt: str = ''
    desc: str = ''
    html_desc: str = ''
    tags: str = ''
    previews: list[Preview] = []
    errors: Errors = Errors()


class UploaderResponse(BaseModel):
    success: bool
    is_s3: bool
    local_link: str
    s3_link: str | None = None
