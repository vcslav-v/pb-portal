from fastapi import APIRouter
from pb_portal.routes.api import sendy


routes = APIRouter()

routes.include_router(sendy.router, prefix='/sendy')
