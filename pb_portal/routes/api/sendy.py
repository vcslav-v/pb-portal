from fastapi import APIRouter, Request

from pb_portal import config
from pb_portal.schemas.sendy import Unsubscribe

router = APIRouter()


@config.logger.catch()
@router.post('/unsubscribe')
async def help(
    request: Request,
    data: Unsubscribe,
):
    config.logger.info(data)
