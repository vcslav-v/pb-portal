import json
import os
from datetime import datetime
from random import randint

import cssutils
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from pb_portal import connectors, mem

STORAGE_URL = os.environ.get('STORAGE_URL', 'https://pixelbuddha.net/storage/m')
STATIC_URL = os.environ.get('STATIC_URL', 'http://127.0.0.1:5002')

app_route = Blueprint('route', __name__, url_prefix='/mail')

auth = HTTPBasicAuth()
users = {
    os.environ.get('FLASK_LOGIN') or 'root': generate_password_hash(
        os.environ.get('FLASK_PASS') or 'pass'
    ),
    os.environ.get('TD_ADMIN_LOGIN') or 'td_root': generate_password_hash(
        os.environ.get('TD_ADMIN_PASS') or 'td_pass'
    ),
    os.environ.get('PB_ADMIN_LOGIN') or 'pb_root': generate_password_hash(
        os.environ.get('PB_ADMIN_PASS') or 'pb_pass'
    ),
}
user_roles = {
    os.environ.get('FLASK_LOGIN') or 'root': ['admin', 'td_admin'],
    os.environ.get('TD_ADMIN_LOGIN') or 'td_root': ['td_admin'],
    os.environ.get('PB_ADMIN_LOGIN') or 'pb_root': ['pb_admin'],
}


@auth.get_user_roles
def get_user_roles(user):
    return user_roles[user]


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app_route.route('/digest', methods=['GET', 'POST'])
@auth.login_required(role=['admin', 'pb_admin'])
def digest():
    ident = str(int(datetime.utcnow().timestamp())) + str(randint(0, int(datetime.utcnow().timestamp())))
    if request.method == 'POST':
        select_type = request.form.get('select_type')
        if select_type == 'premium_big':
            return render_template(
                '_digest_field_big_prem.html',
                ident=ident,
            )
        elif select_type == 'common_big':
            return render_template(
                '_digest_field_big_common.html',
                ident=ident,
            )
        elif select_type == 'product_grid':
            return render_template(
                '_digest_field_grid.html',
                ident=ident,
            )
        elif select_type == 'product_grid_row':
            return render_template(
                '_digest_field_grid_row.html',
                ident=ident,
            )
        elif select_type == 'bee_free':
            return render_template(
                '_digest_field_bee_free.html',
                ident=ident,
            )

    return render_template(
        'digest.html',
        base_url=STATIC_URL,
    )


@logger.catch
@app_route.route('/make_digest', methods=['POST'])
@auth.login_required(role=['admin', 'pb_admin'])
def make_digest():
    content = ''
    num_custom_row = 0
    custom_styles = ''
    block_names = set()
    product_grid = []
    uniq_idents = set()
    for name, data in request.form.to_dict().items():
        block_type, ident, *_ = name.split('|')
        uniq_idents.add(ident)
    num_blocks = len(uniq_idents)
    last_ident = ''
    i = 0
    for name, json_data in request.form.to_dict().items():
        block_type, ident, *_ = name.split('|')
        data = json.loads(json_data)
        if product_grid and last_ident != ident:
            is_only_plus = False not in [row[0].pr_type == 'plus' for row in product_grid]
            content += render_template(
                'digest_mail/_mail_product_grid.html',
                content=list(zip(product_grid[::2], product_grid[1::2])),
                is_only_plus=is_only_plus,
                storage=STORAGE_URL,
            )
            _content, _block_names = add_space_or_affiliate(i, num_blocks)
            i += 1
            content += _content
            block_names = block_names.union(_block_names)
            product_grid = []
            block_names.add('product_grid')
        if block_type == 'premium_big':
            if not data.get('url'):
                break
            if False in [num.isdigit() for num in data.get('gallery')]:
                break
            product = connectors.pb.get_product_info(data.get('url'))
            if product.pr_type != 'premium':
                break
            block_names.add(block_type)
            content += render_template(
                'digest_mail/_mail_premium_big.html',
                content=product,
                galley_num=[int(data.get('gallery')[0])] + [int(num)-1 for num in data.get('gallery')[1:]],
                boarders=[
                    data.get('main_boarder'),
                    data.get('gallery_0_boarder'),
                    data.get('gallery_1_boarder'),
                    data.get('gallery_2_boarder'),
                ],
                promocode=data.get('promocode'),
            )
            _content, _block_names = add_space_or_affiliate(i, num_blocks)
            i += 1
            content += _content
            block_names = block_names.union(_block_names)
        elif block_type == 'common_big':
            if not data.get('url'):
                break
            product = connectors.pb.get_product_info(data.get('url'))
            if product.pr_type not in ['freebie', 'plus', 'article']:
                break
            block_names.add(block_type)
            content += render_template(
                'digest_mail/_mail_common_big.html',
                content=product,
                img_num=int(data.get('img')),
                is_border=data.get('img_border'),
            )
            _content, _block_names = add_space_or_affiliate(i, num_blocks)
            i += 1
            content += _content
            block_names = block_names.union(_block_names)
        elif block_type == 'product_grid':
            if not data.get('url'):
                break
            product = connectors.pb.get_product_info(data.get('url'))
            product_grid.append((product, int(data.get('img')), data.get('img_border')))
        elif block_type == 'bee_free_html':
            soup = BeautifulSoup(data.get('html'))
            styles = {}
            sheet = cssutils.parseString(soup.style.text.replace('\n', '').replace('\t', ''))

            for rule in sheet:
                if rule.typeString == 'MEDIA_RULE':
                    for media_rule in rule.cssRules:
                        selector_row = media_rule.selectorText
                        selectors = selector_row.split(',')
                        stl = media_rule.style.cssText
                        for selector in selectors:
                            styles[selector.strip()] = stl

            rows = soup.find_all('table', attrs={'class': 'row'})
            for row in rows:
                filtered = list(filter(lambda x: 'row-' in x, row.attrs['class']))
                if not filtered:
                    continue
                new_class_name = f'customRow-{num_custom_row}'
                num_custom_row += 1
                row_class = filtered[0]
                for style in styles:
                    if row_class not in style:
                        continue
                    custom_styles += '{selector}\n{{ {style} }}\n\n'.format(
                        selector=style.replace(row_class, new_class_name),
                        style=styles[style],
                    )
                row.attrs['class'] = ['row', new_class_name]
                content += row.prettify()

            _content, _block_names = add_space_or_affiliate(i, num_blocks)
            i += 1
            content += _content
            block_names = block_names.union(_block_names)

        last_ident = ident
    if product_grid:
        is_only_plus = False not in [row[0].pr_type == 'plus' for row in product_grid]
        content += render_template(
            'digest_mail/_mail_product_grid.html',
            content=list(zip(product_grid[::2], product_grid[1::2])),
            storage=STORAGE_URL,
            is_only_plus=is_only_plus,
        )
        block_names.add('product_grid')
    style = ''
    for block_name in block_names:
        if block_name == 'premium_big':
            style += render_template('digest_mail/_style_premium_big.html')
        elif block_name == 'space':
            style += render_template('digest_mail/_style_space.html')
        elif block_name == 'affiliate':
            style += render_template('digest_mail/_style_affiliate.html')
        elif block_name == 'common_big':
            style += render_template('digest_mail/_style_common_big.html')
        elif block_name == 'product_grid':
            style += render_template('digest_mail/_style_product_grid.html')
    style += custom_styles
    page_ident = str(
        int(datetime.utcnow().timestamp()) + randint(0, int(datetime.utcnow().timestamp()))
        )
    mem.set_digest(
        page_ident,
        render_template(
            'digest_mail/_mail_digest.html',
            storage=STORAGE_URL,
            style=style,
            content=content,
        )
    )
    return f'{url_for("mail.show_digest")}?ident={page_ident}'


@logger.catch
@app_route.route('/show_digest', methods=['GET'])
@auth.login_required(role=['admin', 'pb_admin'])
def show_digest():
    return mem.get_digest(request.args.get('ident'))


def add_space_or_affiliate(i: int, data_len: int):
    result = ''
    block_names = set()
    if (i + 2) == data_len:
        result += render_template(
            'digest_mail/_mail_space.html'
        )
        block_names.add('space')
        result += render_template(
            'digest_mail/_mail_affiliate.html',
            storage=STORAGE_URL,
        )
        block_names.add('affiliate')
    if (i + 1) < data_len:
        result += render_template(
            'digest_mail/_mail_space.html'
        )
        block_names.add('space')
    return result, block_names
