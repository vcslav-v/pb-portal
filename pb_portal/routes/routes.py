from fastapi import APIRouter
from pb_portal.routes.local_routes import index

routes = APIRouter()

routes.include_router(index.router, prefix='')
