import os

from flask import Blueprint, render_template, send_file, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app_route = Blueprint('route', __name__, url_prefix='/contracts')

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
@app_route.route('/', methods=['GET', 'POST'])
@auth.login_required(role='admin')
def contracts():
    if request.method == 'POST':
        if request.files.getlist('check_png'):
            connectors.contracts.add_check(
                int(request.form.get('contract_ident')),
                request.files.getlist('check_png'),
            )
        elif request.form.get('type') == 'add':
            connectors.contracts.add_contract(
                connectors.contracts.schemas.Contract(
                    id_selfemployed=int(request.form.get('selfemployer_id')),
                    id_sevice=int(request.form.get('service_id')),
                    ammount=int(request.form.get('new_contract_amount')),
                    contract_date=datetime.strptime(
                        request.form.get('new_contract_date'), '%d-%m-%Y'
                    ).date(),
                )
            )
        elif request.form.get('type') == 'gen':
            connectors.contracts.gen_contracts(
                connectors.contracts.schemas.Contract(
                    id_selfemployed=int(request.form.get('selfemployer_id')),
                    id_sevice=int(request.form.get('service_id')),
                    ammount=int(request.form.get('new_contract_amount')),
                    contract_date=datetime.strptime(
                        request.form.get('new_contract_date'), '%d-%m-%Y'
                    ).date(),
                )
            )
        else:
            connectors.contracts.add_signed_contract(
                request.files.getlist('signed_pdf'),
                int(request.form.get('contract_ident'))
            )
    return render_template(
        'contracts.html',
    )


@logger.catch
@app_route.route('/get-contracts', methods=['POST'])
@auth.login_required(role='admin')
def get_contracts():
    return connectors.contracts.get_contract_page().json()


@logger.catch
@app_route.route('/get-contract', methods=['POST'])
@auth.login_required(role='admin')
def get_contract():
    return send_file(connectors.contracts.get_contract(
        int(request.form.get('contr_ident')),
    ), mimetype='application/pdf')


@logger.catch
@app_route.route('/get-check', methods=['POST'])
@auth.login_required(role='admin')
def get_check():
    return send_file(connectors.contracts.get_check(
        int(request.form.get('contr_ident')),
    ), mimetype='image/png')


@logger.catch
@app_route.route('/get-signed-contract', methods=['POST'])
@auth.login_required(role='admin')
def get_signed_contract():
    return send_file(connectors.contracts.get_signed_contract(
        int(request.form.get('contr_ident')),
    ), mimetype='application/pdf')
