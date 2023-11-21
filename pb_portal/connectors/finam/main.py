import os

import requests
from pb_portal.connectors.finam import schemas
from loguru import logger

NETLOC = os.environ.get('FINAM_NETLOC') or 'http://127.0.0.1:8000'
TOKEN = os.environ.get('FINAM_TOKEN') or 'pass'


def get_сurrencies() -> schemas.Items:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/сurrencies')
        if resp.ok:
            logger.debug(resp.content)
            return schemas.Items.parse_raw(resp.content)
        return schemas.Items()


def get_categories() -> schemas.Node:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/category-tree')
        if resp.ok:
            logger.debug(resp.content)
            return schemas.Node.parse_raw(resp.content)
        return schemas.Node(name='')


def rm_transaction(trans_id):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{NETLOC}/api/rm_transaction?trans_id={trans_id}')
        if not resp.ok:
            raise ValueError


def post_transaction(transaction: schemas.Transaction):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{NETLOC}/api/transaction', data=transaction.model_dump_json().encode('utf-8'))
        logger.debug(resp.content)


def get_page_transactions(data: schemas.GetTransactionPage) -> schemas.TransactionPage:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/transactions', data=data.model_dump_json().encode('utf-8'))
        if resp.ok:
            logger.debug(resp.content)
        return schemas.TransactionPage.parse_raw(resp.content)


def get_page_transaction(trans_id) -> schemas.Transaction:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/transaction?trans_id={trans_id}')
        if resp.ok:
            logger.debug(resp.content)
        return schemas.Transaction.parse_raw(resp.content)


def get_get_short_stat(fr_to: schemas.ShortStat) -> schemas.ShortStat:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/short-stat', data=fr_to.model_dump_json().encode('utf-8'))
        if resp.ok:
            logger.debug(resp.content)
        return schemas.ShortStat.parse_raw(resp.content)


def get_balance() -> schemas.Debts:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/debt')
        if resp.ok:
            logger.debug(resp.content)
        return schemas.Debts.parse_raw(resp.content)


def get_site_stat_data(year: int, site_name: str) -> schemas.FinSiteStat:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/site_stat_data?year={year}&site_name={site_name}')
        logger.debug(resp.content)
        return schemas.FinSiteStat.parse_raw(resp.content)


def get_plus_data() -> schemas.PlusSiteData:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{NETLOC}/api/get_plus_data')
        logger.debug(resp.content)
        return schemas.PlusSiteData.parse_raw(resp.content)
