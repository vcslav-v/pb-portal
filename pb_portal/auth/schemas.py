from fastapi_users import schemas
from enum import Enum
from pydantic import field_validator
from pydantic_core import PydanticCustomError


class UserRoles(int, Enum):
    admin = 1
    manager = 2
    creator = 3
    user = 4


class UserRead(schemas.BaseUser[int]):
    role_id: UserRoles = UserRoles.user


class UserCreate(schemas.BaseUserCreate):
    role_id: UserRoles = UserRoles.user

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise PydanticCustomError(
                'value_error',
                'value is not a valid password: 8 characters required',
                dict(reason='Password must be at least 8 characters long.'),
            )
        return v


class UserUpdate(schemas.BaseUserUpdate):
    pass
