import json
import os
from datetime import datetime

import requests
from loguru import logger
import pb_admin
from pb_admin import schemas as pb_schemas

from pb_portal.connectors.pb import schemas

API_URL = os.environ.get('PB_API_URL', '')
TOKEN = os.environ.get('PB_API_TOKEN', '')
NAME = os.environ.get('PB_API_NAME', '')
PB_STAT_API_URL = os.environ.get('PB_STAT_API_URL', '')
PB_USER_URL = os.environ.get('PB_USER_URL', '')

SITE_URL = os.environ.get('SITE_URL', '')
PB_LOGIN = os.environ.get('PB_LOGIN', '')
PB_PASSWORD = os.environ.get('PB_PASSWORD', '')


@logger.catch()
def get_site_info_of(type_info: str = 'category', _filter: list[str] = []) -> list[str]:
    header = {'Authorization': f'Basic {TOKEN}'}
    resp = requests.get(f'{API_URL}/list/{type_info}', headers=header)
    if resp.ok:
        return list(filter(lambda x: x not in _filter, json.loads(resp.content)))
    return []


@logger.catch()
def get_site_info_of_tags(_filter: list[str] = []) -> dict:
    header = {'Authorization': f'Basic {TOKEN}'}
    resp = requests.get(f'{API_URL}/tag', headers=header)
    if resp.ok:
        result = json.loads(resp.content)
        return {k: v for k, v in result.items() if v not in _filter}
    return {'Actions': [f'tag_{i}' for i in range(20)], 'Graphics': [f'tag_{i}' for i in range(10)] + [f'Gtag_{i}' for i in range(10)]}


@logger.catch
def get_correct_slug(slug: str, product_type: str):
    header = {'Authorization': f'Basic {TOKEN}'}
    data = {'slug': slug, 'type': product_type}
    resp = requests.post(f'{API_URL}/check', headers=header, data=data)
    if resp.ok:
        return json.loads(resp.content)
    return {}


@logger.catch
def get_top_products(start_date: str, end_date: str, limit: int) -> schemas.PBStat:
    headers = {'Authorization': f'Basic {TOKEN}'}
    _start_date = start_date.split('-')
    _start_date.reverse()
    _end_date = end_date.split('-')
    _end_date.reverse()
    json_data = {
        'from': '-'.join(_start_date),
        'to': '-'.join(_end_date),
        'limit': limit,
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
    headers = {'Authorization': f'Basic {TOKEN}'}
    data = {'url': url}
    resp = requests.post(PB_STAT_API_URL.format(target='info'), headers=headers, json=data)
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
    headers = {'Authorization': f'Basic {TOKEN}'}
    json_data = {
        'from': datetime.utcnow().strftime('%Y-%m-%d'),
        'to': datetime.utcnow().strftime('%Y-%m-%d'),
    }
    resp = requests.post(PB_STAT_API_URL.format(target='top/ref'), headers=headers, json=json_data)
    aff_resp = json.loads(resp.text)
    result = schemas.AffiliateInfo()
    idents = []
    for _, affiliate in aff_resp.items():
        result.affilates.append(schemas.Affiliate(
            ident=affiliate['id'],
            name=affiliate['name'],
            url=PB_USER_URL.format(ident=affiliate['id']),
            ref_num=affiliate['num_ref'],
            profit=int(affiliate['sum'] - affiliate['to_pay']),
            to_pay=int(affiliate['to_pay']),
        ))
        result.ref_num += affiliate['num_ref']
        idents.append(affiliate['id'])
    result.aff_num = len(result.affilates)
    for affilate in result.affilates:
        result.profit_sum += affilate.profit
        result.to_pay_sum += affilate.to_pay
    result.affilates.sort(key=lambda x: x.profit, reverse=True)
    return result


def get_categories() -> list[schemas.Category]:
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    categories = pb_session.categories.get_list()
    categories = sorted(categories, key=lambda x: x.weight, reverse=True)
    return categories


def get_products(keyword, category_id, category_name) -> schemas.ProductPage:
    products_page = schemas.ProductPage()
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    products = pb_session.products.get_list(search=keyword, category_id=int(category_id))
    products = sorted(products, key=lambda x: x.created_at, reverse=True)
    products_page.products = products
    products_page.category_name = category_name
    products_page.category_id = int(category_id)
    return products_page


def get_full_products(products: list[schemas.Product]) -> list[schemas.Product]:
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    result = []
    for product in products:
        result.append(
            pb_session.products.get(product.ident, product_type=product.product_type, is_lite=True)
        )
    return result


def search_tag(tag: str) -> pb_schemas.Tag | None:
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    tags = pb_session.tags.get_list(search=tag)
    if tags and tags[0].name == tag.lower():
        return tags[0]
