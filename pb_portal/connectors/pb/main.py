import os

import requests
from loguru import logger
import json
from pb_portal.connectors.pb import schemas

API_URL = os.environ.get('PB_API_URL', '')
TOKEN = os.environ.get('PB_API_TOKEN', '')
NAME = os.environ.get('PB_API_NAME', '')
PB_STAT_API_URL = os.environ.get('PB_STAT_API_URL', '')


@logger.catch()
def get_site_info_of(type_info: str = 'category', _filter: list[str] = []) -> list[str]:
    with requests.sessions.Session() as session:
        session.auth = (NAME, TOKEN)
        resp = session.get(f'{API_URL}/list/{type_info}',)
        if resp.ok:
            return list(filter(lambda x: x not in _filter, json.loads(resp.content)))
    return []


@logger.catch
def get_correct_slug(slug: str, product_type: str):
    header = {'Authorization': f'Bearer {TOKEN}'}
    data = {'slug': slug, 'type': product_type}
    resp = requests.post(f'{API_URL}/check', headers=header, data=data)
    if resp.ok:
        return json.loads(resp.content)
    return {}


@logger.catch
def get_top_products(start_date: str, end_date: str) -> schemas.PBStat:
    headers = {'Authorization': f'Bearer {TOKEN}'}
    _start_date = start_date.split('-')
    _start_date.reverse()
    _end_date = end_date.split('-')
    _end_date.reverse()
    json_data = {
        'from': '-'.join(_start_date),
        'to': '-'.join(_end_date),
    }
    resp = requests.post(PB_STAT_API_URL.format(target='plus'), headers=headers, json=json_data)
    plus_resp = json.loads(resp.text)

    resp = requests.post(PB_STAT_API_URL.format(target='premium'), headers=headers, json=json_data)
    prem_resp = json.loads(resp.text)

    plus = []
    for product in plus_resp:
        plus.append(schemas.PlusTop(
            title=product['plus'],
            url=product['url'],
            downloads=product['count_downloads'],
        ))

    prem_by_profit = []
    for product in prem_resp['sum']:
        prem_by_profit.append(schemas.PremTop(
            title=product['plus'],
            url=product['url'],
            profit=product['sum'],
            sales=product['num_sale'],
        ))

    prem_by_sales = []
    for product in prem_resp['num']:
        prem_by_sales.append(schemas.PremTop(
            title=product['plus'],
            url=product['url'],
            profit=product['sum'],
            sales=product['num_sale'],
        ))

    return schemas.PBStat(
        prem_by_profit=prem_by_profit,
        prem_by_sales=prem_by_sales,
        plus=plus,
    )


def get_product_info(url: str) -> schemas.ProductInfo:
    pass
