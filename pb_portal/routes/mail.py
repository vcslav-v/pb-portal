import os
from datetime import datetime
from random import randint

from flask import Blueprint, render_template, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from pb_portal import connectors

STORAGE_URL = os.environ.get('STORAGE_URL', '')
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
}
user_roles = {
    os.environ.get('FLASK_LOGIN') or 'root': ['admin', 'td_admin'],
    os.environ.get('TD_ADMIN_LOGIN') or 'td_root': ['td_admin'],
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
@auth.login_required(role='admin')
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

    return render_template(
        'digest.html',
        base_url=STATIC_URL,
    )


@logger.catch
@app_route.route('/make_digest', methods=['GET'])
@auth.login_required(role='admin')
def make_digest():
    content = ''
    block_names = set()
    product_grid = []
    uniq_idents = set()
    for name, data in request.args.to_dict().items():
        block_type, ident, *_ = name.split('|')
        uniq_idents.add(ident)
    num_blocks = len(uniq_idents)
    last_ident = ''
    i = 0
    for name, data in request.args.to_dict().items():
        block_type, ident, *_ = name.split('|')
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
            url, promocode, *params = data.split('|')
            galley_num = params[-4:]
            boarders = [bch == 'true' for bch in params[:-3]]
            promocode = promocode.strip()
            if not url:
                break
            if False in [num.isdigit() for num in galley_num]:
                break
            product = connectors.pb.get_product_info(url)
            if product.pr_type != 'premium':
                break
            block_names.add(block_type)
            content += render_template(
                'digest_mail/_mail_premium_big.html',
                content=product,
                galley_num=[int(galley_num[0])] + [int(num)-1 for num in galley_num[1:]],
                boarders=boarders,
                promocode=promocode,
            )
            _content, _block_names = add_space_or_affiliate(i, num_blocks)
            i += 1
            content += _content
            block_names = block_names.union(_block_names)
        elif block_type == 'common_big':
            url, img_num, is_border = data.split('|')
            if not url or not img_num.isdigit():
                break
            img_num = int(img_num)
            is_border = is_border == 'true'
            product = connectors.pb.get_product_info(url)
            if product.pr_type not in ['freebie', 'plus', 'article']:
                break
            block_names.add(block_type)
            content += render_template(
                'digest_mail/_mail_common_big.html',
                content=product,
                img_num=img_num,
                is_border=is_border,
            )
            _content, _block_names = add_space_or_affiliate(i, num_blocks)
            i += 1
            content += _content
            block_names = block_names.union(_block_names)
        elif block_type == 'product_grid':
            url, img_num, is_border = data.split('|')
            if not url or not img_num.isdigit():
                break
            img_num = int(img_num)
            is_border = is_border == 'true'
            product = connectors.pb.get_product_info(url)
            product_grid.append((product, img_num, is_border))
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
    return render_template(
        'digest_mail/_mail_digest.html',
        storage=STORAGE_URL,
        style=style,
        content=content,

    )


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
