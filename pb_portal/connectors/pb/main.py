import json
import os
from datetime import datetime
from urllib.parse import urlparse

import requests
from loguru import logger

from pb_portal.connectors.pb import schemas

API_URL = os.environ.get('PB_API_URL', '')
TOKEN = os.environ.get('PB_API_TOKEN', '')
NAME = os.environ.get('PB_API_NAME', '')
PB_STAT_API_URL = os.environ.get('PB_STAT_API_URL', '')
PB_USER_URL = os.environ.get('PB_USER_URL', '')


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
    resp = requests.post(PB_STAT_API_URL.format(target='top/plus'), headers=headers, json=json_data)
    plus_resp = json.loads(resp.text)

    resp = requests.post(PB_STAT_API_URL.format(target='top/premium'), headers=headers, json=json_data)
    prem_resp = json.loads(resp.text)

    plus = []
    for product in plus_resp:
        plus.append(schemas.PlusTop(
            title=product['title'],
            url=product['url'],
            downloads=product['count_downloads'],
        ))

    prem_by_profit = []
    for product in prem_resp['sum']:
        prem_by_profit.append(schemas.PremTop(
            title=product['title'],
            url=product['url'],
            profit=product['sum'],
            sales=product['num_sale'],
        ))

    prem_by_sales = []
    for product in prem_resp['num']:
        prem_by_sales.append(schemas.PremTop(
            title=product['title'],
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
    headers = {'Authorization': f'Bearer {TOKEN}'}
    url_path = urlparse(url).path
    data = {'slug': url_path.split('/')[-1]}
    resp = requests.post(PB_STAT_API_URL.format(target=f'info'), headers=headers, json=data)
    product_info = json.loads(resp.text)
    return schemas.ProductInfo(
        pr_type=product_info['product_type'],
        url=url,
        title=product_info['title'],
        main_img_url=product_info['material_image'],
        gallery_urls=product_info['gallery'],
        exerpt=product_info['short_desc'],
        regular_price=product_info.get('price'),
        sale_regular_price=product_info.get('sale_price'),
    )


def get_affiliates() -> schemas.AffiliateInfo:
    headers = {'Authorization': f'Bearer {TOKEN}'}
    json_data = {
        'from': datetime.utcnow().strftime('%Y-%m-%d'),
        'to': datetime.utcnow().strftime('%Y-%m-%d'),
    }
    resp = requests.post(PB_STAT_API_URL.format(target='top/ref'), headers=headers, json=json_data)
    aff_resp = json.loads(resp.text)
    result = schemas.AffiliateInfo()
    idents = []
    for affiliate in aff_resp:
        if affiliate['currency'] != 'usd':
            continue
        if affiliate['id'] not in idents:
            result.affilates.append(schemas.Affiliate(
                ident=affiliate['id'],
                name=affiliate['name'],
                url=PB_USER_URL.format(ident=affiliate['id']),
                ref_num=affiliate['num_ref'],
                profit=int(affiliate['sum'] - affiliate['to_pay']),
                to_pay=int(affiliate['to_pay'] if affiliate['accrued'] == 0 else 0),
            ))
            result.ref_num += affiliate['num_ref']
            idents.append(affiliate['id'])
        else:
            for aff in result.affilates:
                if aff.ident != affiliate['id']:
                    continue
                aff.profit -= int(affiliate['to_pay'])
                aff.to_pay += int(affiliate['to_pay'] if affiliate['accrued'] == 0 else 0)
                break
    result.aff_num = len(result.affilates)
    for affilate in result.affilates:
        result.profit_sum += affilate.profit
        result.to_pay_sum += affilate.to_pay
    result.affilates.sort(key=lambda x: x.profit, reverse=True)
    return result
