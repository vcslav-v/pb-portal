import os

from flask import Blueprint, redirect, render_template, send_file, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors
from werkzeug.security import check_password_hash, generate_password_hash

app_route = Blueprint('route', __name__, url_prefix='/contracts')

auth = HTTPBasicAuth()
users = {
    os.environ.get('FLASK_LOGIN', 'root'): generate_password_hash(
        os.environ.get('FLASK_PASS', 'pass')
    ),
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app_route.route('/', methods=['GET', 'POST'])
@auth.login_required
def contracts():
    if request.method == 'POST':
        if request.form.get('check_url'):
            connectors.contracts.add_check(
                int(request.form.get('contract_ident')),
                request.form.get('check_url'),
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
@auth.login_required
def get_contracts():
    return connectors.contracts.get_contract_page().json()


@logger.catch
@app_route.route('/get-contract', methods=['POST'])
@auth.login_required
def get_contract():
    return send_file(connectors.contracts.get_contract(
        int(request.form.get('contr_ident')),
    ), mimetype='image/png')


@logger.catch
@app_route.route('/get-check', methods=['POST'])
@auth.login_required
def get_check():
    return send_file(connectors.contracts.get_check(
        int(request.form.get('contr_ident')),
    ), mimetype='image/png')


@logger.catch
@app_route.route('/get-signed-contract', methods=['POST'])
@auth.login_required
def get_signed_contract():
    return send_file(connectors.contracts.get_signed_contract(
        int(request.form.get('contr_ident')),
    ), mimetype='application/pdf')
