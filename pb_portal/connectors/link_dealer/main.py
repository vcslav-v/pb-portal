import os

import requests
from pb_portal.connectors.link_dealer import schemas
from loguru import logger

URL = os.environ.get('LINK_DEALER_URL', '')
TOKEN = os.environ.get('LINK_DEALER_TOKEN', '')


def get_utm(data: schemas.LinkCreate) -> schemas.Link:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{URL}/api/create_link', data=data.model_dump_json().encode('utf-8'))
        resp.raise_for_status()
        return schemas.Link.model_validate_json(resp.content)


def get_info() -> schemas.Info:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{URL}/api/info')
        resp.raise_for_status()
        return schemas.Info.model_validate_json(resp.content)


def get_last_utms() -> schemas.LastLinks:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{URL}/api/last_links')
        resp.raise_for_status()
        return schemas.LastLinks.model_validate_json(resp.content)
