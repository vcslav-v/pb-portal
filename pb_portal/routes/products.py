import calendar
import os
from datetime import date

from flask import Blueprint, render_template, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from pb_portal import connectors

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
    return user_roles[user]


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app_route.route('/list', methods=['GET', 'POST'])
@auth.login_required(role='admin')
def list():
    if request.method == 'POST':
        page_data = connectors.products.schemas.FilterPage()
        page_data.page = int(request.form.get('page'))

        if request.form.get(
            'end_date_datepicker_start'
        ) and request.form.get(
            'end_date_datepicker_end'
        ):
            end_date_start_mon, end_date_start_year = request.form.get(
                'end_date_datepicker_start'
            ).split('-')
            page_data.end_date_start = date.fromisoformat(
                f'{end_date_start_year}-{end_date_start_mon}-01'
            )
            end_date_end_mon, end_date_end_year = request.form.get(
                'end_date_datepicker_end'
            ).split('-')
            _, end_days_month = calendar.monthrange(int(end_date_end_year), int(end_date_end_mon))
            page_data.end_date_end = date.fromisoformat(
                f'{end_date_end_year}-{end_date_end_mon}-{end_days_month}'
            )

        if request.form.get('designer').isdecimal():
            page_data.designer_id = int(request.form.get('designer'))
        pbd = connectors.products.get_all(page_data)
        return render_template(
            '_product_page.html',
            pbd=pbd,
        )
    else:
        page_data = connectors.products.get_page_data()
        return render_template(
            'product_base.html',
            page_data=page_data
        )
