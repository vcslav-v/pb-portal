import os
from datetime import datetime
from unicodedata import name
from urllib.parse import urlparse

from flask import Blueprint, render_template, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors
from werkzeug.security import check_password_hash, generate_password_hash

MARKETS = connectors.dm_parser.get_markets().market_places

app_route = Blueprint('route', __name__, url_prefix='/products')

auth = HTTPBasicAuth()
users = {
    os.environ.get('FLASK_LOGIN') or 'root': generate_password_hash(
        os.environ.get('FLASK_PASS') or 'pass'
    ),
    os.environ.get('TD_ADMIN_LOGIN') or 'td_root': generate_password_hash(
        os.environ.get('TD_ADMIN_PASS') or 'td_pass'
    ),
}
user_roles = {
    os.environ.get('FLASK_LOGIN') or 'root': ['admin', 'td_admin'],
    os.environ.get('TD_ADMIN_LOGIN') or 'td_root': ['td_admin'],
}

@auth.get_user_roles
def get_user_roles(user):
    return user_roles(user)


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app_route.route('/add', methods=['GET'])
def add():
    return render_template(
        'add_product.html',
        creators=connectors.dm_parser.get_creators().creators,
    )


@logger.catch
@app_route.route('/get_item_field', methods=['POST'])
def get_item_field():
    return render_template(
        '_item_form.html',
        form_ident=int(datetime.utcnow().timestamp()),
        markets=MARKETS,
    )


@logger.catch
@app_route.route('/post_product', methods=['POST'])
def post_product():
    result = connectors.dm_parser.schemas.result()
    product_name = request.form.get('product_name')
    if not product_name:
        result.arg = 'Wrong product_name'
        return result.json()
    creator_id = int(request.form.get('creator_id'))
    product_info = connectors.dm_parser.schemas.product(
        name=product_name,
        creator_id=creator_id,
        is_bundle=True if request.form.get('is_bundle') == 'is_bundle' else False
    )
    items = {}
    urls = set()
    for field in request.form.to_dict():
        if field.split('|')[0] != 'item':
            continue
        ident = field.split('|')[-1]
        key = field.split('|')[1]
        if not items.get(ident):
            items[ident] = {}
        if not request.form.get(field):
            continue
        items[ident][key] = request.form.get(field)
    if not items:
        result.arg = 'No one item'
        return result.json()
    for form_item in items.values():
        if not form_item.get('url'):
            continue
        parsed_url = urlparse(form_item['url'])
        if not parsed_url.netloc:
            result.arg = f'Wrong url {form_item["url"]}'
            return result.json()
        form_item['url'] = parsed_url.geturl()
        if form_item['url'] in urls:
            result.arg = f'Url {form_item["url"]} use twice'
            return result.json()
        urls.add(form_item['url'])
        form_item['account_id'] = int(form_item['account_id'])
        if form_item.get('personal_price'):
            try:
                cents = _make_cents(form_item['personal_price'])
            except Exception:
                result.arg = f'Wrong price {form_item}'
                return result.json()
            form_item['personal_price'] = cents
        if form_item.get('commercial_price'):
            try:
                cents = _make_cents(form_item['commercial_price'])
            except Exception:
                result.arg = f'Wrong price {form_item}'
                return result.json()
            form_item['commercial_price'] = cents
        if form_item.get('extended_price'):
            try:
                cents = _make_cents(form_item['extended_price'])
            except Exception:
                result.arg = f'Wrong price {form_item}'
                return result.json()
            form_item['extended_price'] = cents
        item = connectors.dm_parser.schemas.item(**form_item)
        product_info.items.append(item)

    return connectors.dm_parser.post_product(product_info).json()


def _make_cents(raw_price: str):
    return int(float(raw_price.strip().replace(',', '.')) * 100)
