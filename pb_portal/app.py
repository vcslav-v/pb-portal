import os

from flask import Flask, redirect, render_template, request, url_for, send_file
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash
from pb_portal import connectors

app = Flask(__name__)
auth = HTTPBasicAuth()

app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY') or 'you-will-never-guess'
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


@app.route('/')
@auth.login_required
def index():
    return redirect(url_for('tag_board'))


@logger.catch
@app.route('/tag-board', methods=['GET', 'POST'])
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


@logger.catch
@app.route('/graphics-tools', methods=['GET', 'POST'])
def graphics_tools():
    return render_template(
        'graphics_tools.html',
    )


@logger.catch
@app.route('/tinify', methods=['POST'])
def tinify():
    try:
        zip_file = connectors.graphic.get_tiny_zip(
            request.files.getlist('forTiny'),
            request.form.get('resize_width')
        )
    except Exception as e:
        logger.error(e.args)
        return
    return send_file(zip_file, mimetype='application/x-zip-compressed')


@logger.catch
@app.route('/longy', methods=['POST'])
def longy():
    try:
        long_jpg = connectors.graphic.get_long_jpg(
            request.files.getlist('forLong'),
        )
    except Exception as e:
        logger.error(e.args)
        return
    return send_file(long_jpg, mimetype='image/jpeg')
