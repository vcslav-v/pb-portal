from pydantic import BaseModel
from typing import Optional


class creator(BaseModel):
    ident: int
    name: str


class creators(BaseModel):
    creators: list[creator] = []


class market_place(BaseModel):
    account_ident: int
    account_name: str
    market_name: str


class market_places(BaseModel):
    market_places: list[market_place] = []


class item(BaseModel):
    url: str
    account_id: int
    personal_price: Optional[int] = None
    commercial_price: Optional[int] = None
    extended_price: Optional[int] = None
    name: Optional[str] = None
    cattegories: Optional[list[str]] = []
    ident: Optional[int] = None


class product(BaseModel):
    name: str
    creator_id: int
    is_bundle: bool
    items: list[item] = []


class result(BaseModel):
    arg: str = 'API problem'
    status: int = 500
