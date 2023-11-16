from pydantic import BaseModel, field_validator, ValidationError, ValidationInfo
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

    @field_validator('text_colour', 'background_color', mode='before')
    def must_be_color_like(cls, value, info: ValidationInfo):
        matches = re.match(RE_COLOUR, value, re.IGNORECASE)
        if matches:
            return matches.group(0)
        else:
            raise ValidationError('background color is wrong')

    @field_validator('final_text', 'title',  mode='before')
    def must_be_raws_list(cls, value, info: ValidationInfo):
        if '\r\n' in value:
            return value.split('\r\n')
        else:
            return value.split('\n')

    @field_validator('time_cover', 'time_shot', 'time_final',  mode='before')
    def must_be_float(cls, value, info: ValidationInfo):
        return float(value)


class Item(BaseModel):
    uid: int
    name: str
    date: datetime
    link: Optional[str] = None
    in_working: bool


class Page(BaseModel):
    items: list[Item] = []
