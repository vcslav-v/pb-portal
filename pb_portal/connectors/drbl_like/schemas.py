"""Pydantic's models."""
from pydantic import BaseModel


class Task(BaseModel):
    """Task model."""
    id: int
    link: str
    targ_like: int
    done_like: int


class LikerPage(BaseModel):
    """Liker page model."""
    total_accounts: int = 0
    in_work_accs: int = 0
    target_accounts: int = 0
    tasks: list[Task] = []
