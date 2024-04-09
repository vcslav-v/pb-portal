from fastapi import APIRouter
from pb_portal.routes.pages import index
from pb_portal.routes.user import auth
from pb_portal.auth.schemas import UserRead, UserCreate
from pb_portal.auth.backend import auth_backend
from pb_portal.auth.tools import fastapi_users

routes = APIRouter()

routes.include_router(index.router, prefix='', tags=['pages'])
routes.include_router(auth.router, prefix='/user', tags=['user'])

routes.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
routes.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
