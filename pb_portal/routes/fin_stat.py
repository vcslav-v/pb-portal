import json
import os

from flask import Blueprint, render_template, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors
from werkzeug.security import check_password_hash, generate_password_hash

app_route = Blueprint('route', __name__, url_prefix='/fin_stat')

auth = HTTPBasicAuth()
users = {
    os.environ.get('FLASK_LOGIN') or 'root': generate_password_hash(
        os.environ.get('FLASK_PASS') or 'pass'
    ),
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app_route.route('/', methods=['GET'])
@auth.login_required
def fin_stat():
    graph = {'data': [
        {
            'x': ['01-2020', '02-2020', '03-2020', '04-2020', '05-2020', '06-2020', '07-2020', '08-2020', '09-2020', '10-2020', '11-2020', '12-2020'],
            'y': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'name': 'Plus',
            'type': 'bar'
        },
        {
            'x': ['01-2020', '02-2020', '03-2020', '04-2020', '05-2020', '06-2020', '07-2020', '08-2020', '09-2020', '10-2020', '11-2020', '12-2020'],
            'y': [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            'name': 'Freebie',
            'type': 'bar'
        },
        {
            'x': ['01-2020', '02-2020', '03-2020', '04-2020', '05-2020', '06-2020', '07-2020', '08-2020', '09-2020', '10-2020', '11-2020', '12-2020'],
            'y': [5, 3, 2, 6, 1, 7, 8, 5, 2, 3, 2, 5],
            'name': "Employ's bonuses",
            'type': 'bar'
        },
        {
            'x': ['01-2020', '02-2020', '03-2020', '04-2020', '05-2020', '06-2020', '07-2020', '08-2020', '09-2020', '10-2020', '11-2020', '12-2020'],
            'y': [4, 3, 6, 9, 8, 7, 1, 5, 12, 3, 2, 11],
            'name': 'Develop',
            'type': 'bar'
        }
    ]}
    income_graph_json = json.dumps(graph)
    expense_graph_json = json.dumps(graph)
    return render_template(
        'money_stat.html',
        income_graph_json=income_graph_json,
        expense_graph_json=expense_graph_json,
    )


@logger.catch
@app_route.route('/get_site_stat_data', methods=['POST'])
@auth.login_required
def get_site_stat_data():
    year = int(request.form.get('year'))
    page_data = connectors.finam.get_site_stat_data(year)
    return page_data.json()
