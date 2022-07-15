import os

import requests
import io
from pb_portal.connectors.contracts import schemas
from loguru import logger

API_URL = os.environ.get('CONTRACT_URL') or 'http://127.0.0.1:8000'
TOKEN = os.environ.get('CONTRACT_TOKEN') or 'pass'


def get_contract_page() -> schemas.Page:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/get-page')
        logger.debug(resp.content)
        if resp.ok:
            return schemas.Page.parse_raw(resp.content)
        return schemas.Page()


def get_contract(ident: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/get-contract?ident={ident}')
        contract_file = io.BytesIO(resp.content)
        return contract_file


def get_check(ident: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/get-check?ident={ident}')
        check_file = io.BytesIO(resp.content)
        return check_file


def get_signed_contract(ident: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/get-signed-contract?ident={ident}')
        signed_contract_file = io.BytesIO(resp.content)
        return signed_contract_file
