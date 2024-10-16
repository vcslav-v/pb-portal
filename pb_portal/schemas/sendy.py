from pydantic import BaseModel


class Unsubscribe(BaseModel):
    name: str | None = None
    email: str | None = None
    list_id: str | None = None
    list_name: str | None = None
    list_url: str | None = None
    gravatar: str | None = None
