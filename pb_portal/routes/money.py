import os
from datetime import datetime, date, timedelta
import calendar

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


try:
    CATEGORIES = connectors.finam.get_categories()
except Exception:
    CATEGORIES = connectors.finam.schemas.Node(name='root')
if CATEGORIES.children:
    ACCOUNTS = next(filter(lambda x: x.name == 'Balance', CATEGORIES.children))
    INCOME = next(filter(lambda x: x.name == 'Income', CATEGORIES.children))
    EXPENSE = next(filter(lambda x: x.name == 'Expense', CATEGORIES.children))
else:
    ACCOUNTS, INCOME, EXPENSE = [CATEGORIES] * 3


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app_route.route('/', methods=['GET'])
@auth.login_required(role='admin')
def money():
    сurrencies = connectors.finam.get_сurrencies()
    return render_template(
        'money.html',
        сurrencies=сurrencies,
        categories=CATEGORIES,
        accounts_cat=ACCOUNTS,
        income_cat=INCOME,
        expence_cat=EXPENSE,
    )


@logger.catch
@app_route.route('/post-transaction', methods=['POST'])
@auth.login_required(role='admin')
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
    from_cattegory_id = request.form.get('from_money')
    if from_cattegory_id:
        logger.debug(ACCOUNTS.children)
        debt_k = ((len(ACCOUNTS.children) - 1) / len(ACCOUNTS.children))
        debt_value = int(float(request.form.get('sum').replace(',', '.')) * debt_k * 100)
        balance_transaction = connectors.finam.schemas.Transaction(
            date=datetime.strptime(request.form.get('date'), '%d-%m-%Y').date(),
            value=debt_value,
            comment=request.form.get('comment'),
            currency_id=int(request.form.get('сurrency')),
            category_id=int(from_cattegory_id),
        )
        connectors.finam.post_transaction(balance_transaction)

    return jsonify({'ok': 200})


@logger.catch
@app_route.route('/rm-transaction', methods=['POST'])
def rm_transaction():
    connectors.finam.rm_transaction(request.form.get('trans_id'))
    return jsonify({'ok': 200})


@logger.catch
@app_route.route('/get-transactions', methods=['POST'])
@auth.login_required(role='admin')
def get_transactions():
    data = schemas.GetTransactionPage(
        from_date=datetime.strptime(request.form.get('from_date'), '%d-%m-%Y').date()
    )
    if request.form.get('page'):
        data.page = int(request.form.get('page'))
    if request.form.get('search_req').strip():
        data.req_str = request.form.get('search_req').strip()
    transactions = connectors.finam.get_page_transactions(data)
    return transactions.json()


@logger.catch
@app_route.route('/get-transaction', methods=['POST'])
@auth.login_required(role='admin')
def get_transaction():
    trans_id = request.form.get('trans_id')
    transaction = connectors.finam.get_page_transaction(trans_id)
    return transaction.json()


@logger.catch
@app_route.route('/get_categories', methods=['POST'])
def get_categories():
    flat_cat = tools.get_flat_cat(CATEGORIES)
    return jsonify(flat_cat)


@logger.catch
@app_route.route('/get-short-stat', methods=['POST'])
@auth.login_required(role='admin')
def get_short_stat():
    first_col_month_start, first_col_year_start = request.form.get('first_stat_start').split('-')
    first_col_date_from = date.fromisoformat(f'{first_col_year_start}-{first_col_month_start}-01')

    first_col_month_end, first_col_year_end = request.form.get('first_stat_end').split('-')
    _, end_days_month = calendar.monthrange(int(first_col_year_end), int(first_col_month_end))
    first_col_date_to = date.fromisoformat(f'{first_col_year_end}-{first_col_month_end}-{end_days_month}')
    first_col_dates = connectors.finam.schemas.ShortStat(
        frm=first_col_date_from,
        to=first_col_date_to,
    )
    first_col = connectors.finam.get_get_short_stat(first_col_dates)

    sec_col_month_start, sec_col_year_start = request.form.get('sec_stat_start').split('-')
    sec_col_date_from = date.fromisoformat(f'{sec_col_year_start}-{sec_col_month_start}-01')
    sec_col_month_end, sec_col_year_end = request.form.get('sec_stat_end').split('-')
    _, end_days_month = calendar.monthrange(int(sec_col_year_end), int(sec_col_month_end))
    sec_col_date_to = date.fromisoformat(f'{sec_col_year_end}-{sec_col_month_end}-{end_days_month}')
    sec_col_dates = connectors.finam.schemas.ShortStat(
        frm=sec_col_date_from,
        to=sec_col_date_to,
    )
    sec_col = connectors.finam.get_get_short_stat(sec_col_dates)
    return jsonify({'first_col': first_col.dict(), 'sec_col': sec_col.dict()})


@logger.catch
@app_route.route('/get_balance', methods=['POST'])
def get_balance():
    debt = connectors.finam.get_balance()
    return debt.json()


@logger.catch
@app_route.route('/get_stats_selector', methods=['POST'])
def get_stats_selector():
    cur_date = datetime.now().date()
    start_cur_month = date(cur_date.year, cur_date.month, 1)
    last_month_end = start_cur_month - timedelta(days=1)
    start_last_month = date(last_month_end.year, last_month_end.month, 1)
    stat_date = {
        'cur_month': {
            'name': cur_date.strftime("%B"),
            'value': f'{start_cur_month.isoformat()}/{cur_date.isoformat()}'
        },
        'last_month': {
            'name': last_month_end.strftime("%B"),
            'value': f'{start_last_month.isoformat()}/{last_month_end.isoformat()}'
        },
    }
    for q_num, mnth in enumerate(range(1, 12, 3), start=1):
        q_start = date(cur_date.year, mnth, 1)
        if q_start > cur_date:
            break
        if mnth + 4 < 12:
            q_end = date(cur_date.year, mnth + 3, 1) - timedelta(days=1)
        else:
            q_end = date(cur_date.year + 1, 1, 1) - timedelta(days=1)
        stat_date[f'Q{q_num}'] = {
            'name': f'Q{q_num}-{q_start.year}',
            'value': f'{q_start.isoformat()}/{q_end.isoformat()}'
        }
    year_names = {0: 'cur_year', 1: 'last_year', 2: 'last_last_year'}
    for num_past_year in range(3):
        start_year = date(cur_date.year - num_past_year, 1, 1)
        end_year = date(cur_date.year - num_past_year, 12, 31)
        stat_date[year_names[num_past_year]] = {
            'name': str(start_year.year),
            'value': f'{start_year.isoformat()}/{end_year.isoformat()}'
        }
    return jsonify(stat_date)
