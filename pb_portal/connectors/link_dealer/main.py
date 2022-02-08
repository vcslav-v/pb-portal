import os

import requests
from pb_portal.connectors.link_dealer import schemas
from loguru import logger

URL = os.environ.get('LINK_DEALER_URL') or 'http://127.0.0.1:8000'
TOKEN = os.environ.get('LINK_DEALER_TOKEN') or 'pass'


def get_utm(link, source, item_type, project) -> schemas.utms:
    with requests.sessions.Session() as session:
        if not project or project.isspace():
            project = 'pb'
        session.auth = ('root', TOKEN)
        data = {
            "link": link,
            "source": source,
            "project": project,
            "item_type": item_type
        }
        resp = session.post(f'{URL}/api/make-utm', json=data)
        if resp.ok:
            logger.debug(resp.content)
            return schemas.utms.parse_raw(resp.content)
        return schemas.utms()
