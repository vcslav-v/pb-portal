import os

import requests
from pb_portal.connectors.products import schemas
from loguru import logger

API_URL = os.environ.get('PRODUCTS_URL', '')
TOKEN = os.environ.get('PRODUCTS_TOKEN', '')


def get_all() -> schemas.ProductPage:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{API_URL}/api/products')
        logger.debug(resp.content)
        if resp.ok:
            return schemas.ProductPage.parse_raw(resp.content)
        return schemas.ProductPage()
