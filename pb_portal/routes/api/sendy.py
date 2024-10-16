from fastapi import APIRouter, Request

from pb_portal import config, sendy
from urllib.parse import parse_qs

router = APIRouter()


@config.logger.catch()
@router.post('/unsubscribe')
async def unsubscribe(
    request: Request,
):
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')
    body_dict = parse_qs(body_str)
    email = body_dict.get('email', None)
    if email:
        email = email[0]
        sendy.add_unsubscribe_list(email)


@config.logger.catch()
@router.post('/subscribe')
async def subscribe(
    request: Request,
):
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')
    body_dict = parse_qs(body_str)
    email = body_dict.get('email', None)
    if email:
        email = email[0]
        sendy.rm_unsubscribe_list(email)
