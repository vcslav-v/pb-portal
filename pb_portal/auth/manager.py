from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, models, schemas

from pb_portal.db.models import User
from pb_portal.db.tools import get_user_db
from pb_portal.auth.schemas import UserRoles
from pb_portal.config import logger

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        user_create.role_id = UserRoles.user.value
        return await super().create(user_create, safe, request)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
