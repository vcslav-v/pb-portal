from fastapi import APIRouter
from pb_portal.routes.pages import index
from pb_portal.routes.auth import auth

routes = APIRouter()

routes.include_router(index.router, prefix='')
routes.include_router(auth.router, prefix='/login')
