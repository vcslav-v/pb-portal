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


def add_signed_contract(files_data, ident):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        file_data = files_data[0]
        files = {
            'signed_contract': (file_data.filename, file_data.stream, file_data.content_type),
        }
        params = {
            'ident_contract': ident,
        }
        session.post(
            f'{API_URL}/api/add-signed-contract',
            params=params,
            files=files,
        )


def add_check(ident, files_data):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        file_data = files_data[0]
        files = {
            'check': (file_data.filename, file_data.stream, file_data.content_type),
        }
        params = {
            'ident_contract': ident,
        }
        session.post(
            f'{API_URL}/api/add-check',
            params=params,
            files=files
        )


def add_contract(new_contract: schemas.Contract):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        session.post(
            f'{API_URL}/api/make-contract',
            data=new_contract.model_dump_json().encode('utf-8'),
        )


def gen_contracts(new_contract: schemas.Contract):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        session.post(
            f'{API_URL}/api/make-contracts',
            data=new_contract.model_dump_json().encode('utf-8'),
        )
