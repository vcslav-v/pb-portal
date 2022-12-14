import os

import requests
from pb_portal.connectors.products import schemas
from loguru import logger

API_URL = os.environ.get('PRODUCTS_URL', '')
TOKEN = os.environ.get('PRODUCTS_TOKEN', '')


def get_all(page_data: schemas.FilterPage) -> schemas.ProductPage:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/products', data=page_data.json())
        logger.debug(resp.content)
        if resp.ok:
            return schemas.ProductPage.parse_raw(resp.content)
        return schemas.ProductPage()


def get_page_data() -> schemas.ProductPageData:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{API_URL}/api/common_data')
        logger.debug(resp.content)
        if resp.ok:
            return schemas.ProductPageData.parse_raw(resp.content)
        return schemas.ProductPageData()
