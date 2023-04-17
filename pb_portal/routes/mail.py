import os
from datetime import datetime
from random import randint

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
    data = connectors.mailer.schemas.PbDigest(data=request.form.to_dict())
    result = connectors.mailer.make_digest(data)
    page_ident = str(
        int(datetime.utcnow().timestamp()) + randint(0, int(datetime.utcnow().timestamp()))
        )
    mem.set_digest(
        page_ident,
        result,
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
