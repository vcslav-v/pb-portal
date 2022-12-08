import os

import requests
from pb_portal.connectors.neuro import schemas
from loguru import logger

API_URL = os.environ.get('NEURO_URL', '')
TOKEN = os.environ.get('NEURO_TOKEN', '')


def get_gpt_text(params: schemas.TextGPT) -> list[str]:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/get_text', data=params.json())
        logger.debug(resp.content)
        if resp.ok:
            return [option.strip().replace('\\n', ' ').replace('\\', '') for option in resp.text.strip('"').split('||')]
        return ['Error']
