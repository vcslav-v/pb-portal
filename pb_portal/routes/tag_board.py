import os

from flask import Blueprint, render_template, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors
from werkzeug.security import check_password_hash, generate_password_hash

app_route = Blueprint('route', __name__, url_prefix='/tag-board')

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
@app_route.route('/', methods=['GET', 'POST'])
@auth.login_required
def tag_board():
    search_result = connectors.tag_board.schemas.SearchResult(
        items=[],
        tags_stat=[]
    )
    if request.method == 'POST':
        btn = request.form.get('btn')
        search_resp = request.form.get('search_resp')
        xlsx_files = request.files.getlist('xlsx')
        if btn == 'search_by_title' and search_resp:
            search_result = connectors.tag_board.get_items_by_title(search_resp)
        elif btn == 'search_by_tag' and search_resp:
            search_result = connectors.tag_board.get_items_by_tag(search_resp)
        elif btn == 'upload' and xlsx_files:
            for xlsx_file in xlsx_files:
                connectors.tag_board.push_xlsx(xlsx_file)
    return render_template(
        'tag_board.html',
        search_result=search_result,
    )
