from fastapi import APIRouter, Depends
from pb_portal.routes.pages import index, agreement, help
from pb_portal.routes.user import user
from pb_portal.routes.products import products
from pb_portal.routes.api import api_routes
from pb_portal.auth.schemas import UserRead, UserCreate
from pb_portal.auth.backend import auth_backend
from pb_portal.auth.tools import fastapi_users, current_superuser


routes = APIRouter()

routes.include_router(index.router, prefix='', tags=['pages'])
routes.include_router(agreement.router, prefix='/agreement', tags=['pages'])
routes.include_router(products.router, prefix='/products', tags=['products'])
routes.include_router(help.router, prefix='/help', tags=['pages'])
routes.include_router(user.router, prefix='/user', tags=['user'])
routes.include_router(api_routes.routes, prefix='/api', tags=['api'])

routes.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
routes.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(current_superuser)],  # Only superusers can create new users
)
