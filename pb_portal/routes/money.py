import os
from datetime import datetime

from flask import Blueprint, flash, jsonify, render_template, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors, tools
from pb_portal.connectors.finam import schemas
from werkzeug.security import check_password_hash, generate_password_hash

app_route = Blueprint('route', __name__, url_prefix='/money')

auth = HTTPBasicAuth()
users = {
    os.environ.get('FLASK_LOGIN') or 'root': generate_password_hash(
        os.environ.get('FLASK_PASS') or 'pass'
    ),
}

CATEGORIES = connectors.finam.get_categories()


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app_route.route('/', methods=['GET'])
@auth.login_required
def money():
    сurrencies = connectors.finam.get_сurrencies()
    return render_template(
        'money.html',
        сurrencies=сurrencies,
        categories=CATEGORIES,
    )


@logger.catch
@app_route.route('/post-transaction', methods=['POST'])
@auth.login_required
def post_transaction():
    req_cats = []
    for key, value in request.form.to_dict().items():
        if key[:4] == 'cat-' and value != 'temp':
            req_cats.append(int(value))
    try:
        value = int(float(request.form.get('sum').replace(',', '.')) * 100)
    except ValueError:
        flash('Amount of money is wrong')
    if not req_cats:
        flash('Category is wrong')
    transaction = connectors.finam.schemas.Transaction(
        date=datetime.strptime(request.form.get('date'), '%d-%m-%Y').date(),
        value=value,
        comment=request.form.get('comment'),
        currency_id=int(request.form.get('сurrency')),
        category_id=tools.get_youngest_child(req_cats, CATEGORIES),
    )
    if request.form.get('trans_id'):
        transaction.id = request.form.get('trans_id')
    connectors.finam.post_transaction(transaction)
    return jsonify({'ok': 200})


@logger.catch
@app_route.route('/rm-transaction', methods=['POST'])
def rm_transaction():
    connectors.finam.rm_transaction(request.form.get('trans_id'))
    return jsonify({'ok': 200})


@logger.catch
@app_route.route('/get-transactions', methods=['POST'])
@auth.login_required
def get_transactions():
    data = schemas.GetTransactionPage(
        from_date=datetime.strptime(request.form.get('from_date'), '%d-%m-%Y').date()
    )
    if request.form.get('page'):
        data.page = int(request.form.get('page'))
    transactions = connectors.finam.get_page_transactions(data)
    return transactions.json()


@logger.catch
@app_route.route('/get-transaction', methods=['POST'])
@auth.login_required
def get_transaction():
    trans_id = request.form.get('trans_id')
    transaction = connectors.finam.get_page_transaction(trans_id)
    return transaction.json()


@logger.catch
@app_route.route('/get-short-stat', methods=['POST'])
@auth.login_required
def get_short_stat():
    transaction = connectors.finam.get_get_short_stat()
    return transaction.json()


@logger.catch
@app_route.route('/get_categories', methods=['POST'])
def get_categories():
    flat_cat = tools.get_flat_cat(CATEGORIES)
    return jsonify(flat_cat)
