import os

import requests
from loguru import logger
import json

API_URL = os.environ.get('PB_API_URL', '')
TOKEN = os.environ.get('PB_API_TOKEN', '')
NAME = os.environ.get('PB_API_NAME', '')


@logger.catch()
def get_site_info_of(type_info: str = 'category', _filter: list[str] = []) -> list[str]:
    with requests.sessions.Session() as session:
        session.auth = (NAME, TOKEN)
        resp = session.get(f'{API_URL}/list/{type_info}',)
        if resp.ok:
            return list(filter(lambda x: x in _filter, json.loads(resp.content)))
    return []


@logger.catch
def get_correct_slug(slug: str, product_type: str):
    header = {'Authorization': f'Bearer {TOKEN}'}
    data = {'slug': slug, 'type': product_type}
    resp = requests.post(f'{API_URL}/check', headers=header, data=data)
    if resp.ok:
        return json.loads(resp.content)
    return {}
