from fastapi import APIRouter, Request

from pb_portal import config
from pb_portal.schemas.sendy import Unsubscribe
from urllib.parse import parse_qs

router = APIRouter()


@config.logger.catch()
@router.post('/unsubscribe')
async def help(
    request: Request,
):
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')
    body_dict = parse_qs(body_str)
    config.logger.info(body_dict)
