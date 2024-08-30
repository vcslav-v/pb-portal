from typing import Optional

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, IntegerIDMixin, models, schemas

from pb_portal.db.models import User
from pb_portal.db.tools import get_user_db
from pb_portal.auth.schemas import UserRoles
from pb_portal.config import logger, USER_MANAGER_SECRET




class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = USER_MANAGER_SECRET
    verification_token_secret = USER_MANAGER_SECRET

    async def on_after_login(
        self,
        user: models.UP,
        request: Optional[Request] = None,
        response: Optional[Response] = None
    ):
        logger.info(f"User {user.id} has login.")

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
