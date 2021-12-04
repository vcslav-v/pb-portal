import os

import requests
from pb_portal.connectors.finam import schemas
from loguru import logger

NETLOC = os.environ.get('FINAM_NETLOC') or '127.0.0.1:8000'
TOKEN = os.environ.get('FINAM_TOKEN') or 'pass'


def get_сurrencies() -> schemas.Items:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/сurrencies')
        if resp.ok:
            logger.debug(resp.content)
            return schemas.Items.parse_raw(resp.content)
        return schemas.Items()


def get_categories() -> schemas.Node:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/category-tree')
        if resp.ok:
            logger.debug(resp.content)
            return schemas.Node.parse_raw(resp.content)
        return schemas.Node(name='')


def rm_transaction(trans_id):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'https://{NETLOC}/api/rm_transaction?trans_id={trans_id}')
        if not resp.ok:
            raise ValueError


def post_transaction(transaction: schemas.Transaction):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'https://{NETLOC}/api/transaction', data=transaction.json())
        logger.debug(resp.content)


def get_page_transactions(data: schemas.GetTransactionPage) -> schemas.TransactionPage:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/transactions', data=data.json())
        if resp.ok:
            logger.debug(resp.content)
        return schemas.TransactionPage.parse_raw(resp.content)


def get_page_transaction(trans_id) -> schemas.Transaction:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/transaction?trans_id={trans_id}')
        if resp.ok:
            logger.debug(resp.content)
        return schemas.Transaction.parse_raw(resp.content)


def get_get_short_stat() -> schemas.ShortStat:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/short-stat')
        if resp.ok:
            logger.debug(resp.content)
        return schemas.ShortStat.parse_raw(resp.content)
