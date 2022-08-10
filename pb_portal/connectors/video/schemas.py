from pydantic import BaseModel, validator, ValidationError
import re
from datetime import datetime
from typing import Optional

RE_COLOUR = r"#?([a-f]|\d){6}"


class Template1(BaseModel):
    background_color: str
    text_colour: str
    title: list[str]
    sub_title: str
    final_text: list[str]
    time_cover: float
    time_shot: float
    time_final: float
    music: str

    @validator('text_colour', 'background_color', pre=True)
    def must_be_color_like(cls, field):
        matches = re.match(RE_COLOUR, field, re.IGNORECASE)
        if matches:
            return matches.group(0)
        else:
            raise ValidationError('background color is wrong')

    @validator('final_text', 'title', pre=True)
    def must_be_raws_list(cls, field):
        if '\r\n' in field:
            return field.split('\r\n')
        else:
            return field.split('\n')

    @validator('time_cover', 'time_shot', 'time_final', pre=True)
    def must_be_float(cls, field):
        return float(field)


class Item(BaseModel):
    uid: int
    name: str
    date: datetime
    link: Optional[str]
    in_working: bool


class Page(BaseModel):
    items: list[Item] = []
