import os

import requests
from pb_portal.connectors.dm_parser import schemas
from loguru import logger

URL = os.environ.get('PRODUCT_BASE_URL') or 'http://127.0.0.1:8000'
TOKEN = os.environ.get('PRODUCT_BASE_TOKEN') or 'pass'


def get_creators() -> schemas.creators:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{URL}/api/get_creators')
        logger.debug(resp.content)
        if resp.ok:
            logger.debug(resp.content)
            return schemas.creators.parse_raw(resp.content)
        return schemas.creators()


def get_markets() -> schemas.market_places:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{URL}/api/get_markets')
        if resp.ok:
            logger.debug(resp.content)
            return schemas.market_places.parse_raw(resp.content)
        return schemas.market_places()


def post_product(product_info: schemas.product) -> schemas.result:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{URL}/api/post_product', data=product_info.model_dump_json().encode('utf-8'))
        if resp.ok:
            logger.debug(resp.content)
            return schemas.result.parse_raw(resp.content)
        return schemas.result()
