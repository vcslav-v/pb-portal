import os
from loguru import logger
import requests

from pb_portal.connectors.mailer import schemas


URL = os.environ.get('MAILER_URL', 'http://127.0.0.1:8000')
TOKEN = os.environ.get('MAILER_TOKEN', 'pass')


@logger.catch
def make_digest(digest: schemas.PbDigest) -> str:
    """Make digest."""
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{URL}/make_digest', data=digest.json())
        if resp.ok:
            result = schemas.HTML.parse_raw(resp.text)
            logger.debug(resp.content)
            return result.result
        return 'error'
