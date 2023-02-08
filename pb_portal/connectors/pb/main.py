import os

import requests
from loguru import logger
import json

API_URL = os.environ.get('PB_API_URL', '')
TOKEN = os.environ.get('PB_API_TOKEN', '')
NAME = os.environ.get('PB_API_NAME', '')


@logger.catch()
def get_site_info_of(type_info: str = 'category') -> list[str]:
    with requests.sessions.Session() as session:
        session.auth = (NAME, TOKEN)
        resp = session.get(f'{API_URL}/{type_info}',)
        if resp.ok:
            return json.loads(resp.content)
    return []
