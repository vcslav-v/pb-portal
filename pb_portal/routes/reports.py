import os

from flask import Blueprint, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors
from werkzeug.security import check_password_hash, generate_password_hash

app_route = Blueprint('route', __name__, url_prefix='/reports')

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
@app_route.route('/PB-finance', methods=['GET'])
@auth.login_required(role='admin')
def fin_stat():
    name = 'PB'
    return render_template(
        'money_stat.html',
        name=name,
        api_url=url_for('reports.get_site_stat_data'),
    )


@logger.catch
@app_route.route('/PB-stat', methods=['GET', 'POST'])
@auth.login_required(role='admin')
def pb_stat():
    if request.method == 'POST':
        page_data = connectors.pb.get_top_products(
            start_date=request.form.get('fromDate'),
            end_date=request.form.get('toDate'),
        )
        return render_template(
            '_pb_report.html',
            page_data=page_data,
        )
    return render_template(
        'pb_report.html',
    )


@logger.catch
@app_route.route('/PB-affiliates', methods=['GET'])
@auth.login_required(role=['admin', 'pb_admin'])
def pb_affiliates():
    content = connectors.pb.get_affiliates()
    return render_template(
        'affiliates.html',
        content=content,
    )


@logger.catch
@app_route.route('/TD-finance', methods=['GET'])
@auth.login_required(role=['admin', 'td_admin'])
def fin_stat_td():
    name = 'TD'
    return render_template(
        'money_stat.html',
        name=name,
        api_url=url_for('reports.get_site_stat_data'),
    )


@logger.catch
@app_route.route('/PB-plus', methods=['GET'])
@auth.login_required(role='admin')
def plus_report():
    name = 'Plus'
    return render_template(
        'plus_report.html',
        name=name,
        api_url=url_for('reports.get_plus_data'),
    )


@logger.catch
@app_route.route('/get_site_stat_data', methods=['POST'])
@auth.login_required(role=['admin', 'td_admin'])
def get_site_stat_data():
    year = int(request.form.get('year'))
    site_name = request.form.get('site_name')
    page_data = connectors.finam.get_site_stat_data(year, site_name)
    return page_data.json()


@logger.catch
@app_route.route('/get-plus-data', methods=['POST'])
@auth.login_required(role='admin')
def get_plus_data():
    page_data = connectors.finam.get_plus_data()
    return page_data.json()
