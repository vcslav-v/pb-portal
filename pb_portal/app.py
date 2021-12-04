import os

from flask import Flask, redirect, render_template, request, url_for, send_file, flash, jsonify
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash
from pb_portal import connectors, tools
from urllib.parse import urlparse
import json
from datetime import datetime

from pb_portal.connectors.finam import schemas

app = Flask(__name__)
auth = HTTPBasicAuth()

app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY') or 'you-will-never-guess'
users = {
    os.environ.get('FLASK_LOGIN') or 'root': generate_password_hash(
        os.environ.get('FLASK_PASS') or 'pass'
    ),
}

CATEGORIES = connectors.finam.get_categories()


def is_dribbble_link(uri):
    try:
        result = urlparse(uri)
        return result.netloc == 'dribbble.com'
    except AttributeError:
        return False


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
@app.route('/money', methods=['GET'])
@auth.login_required
def money():
    сurrencies = connectors.finam.get_сurrencies()
    return render_template(
        'money.html',
        сurrencies=сurrencies,
        categories=CATEGORIES,
    )


@logger.catch
@app.route('/post-transaction', methods=['POST'])
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
@app.route('/rm-transaction', methods=['POST'])
def rm_transaction():
    connectors.finam.rm_transaction(request.form.get('trans_id'))
    return jsonify({'ok': 200})


@logger.catch
@app.route('/get-transactions', methods=['POST'])
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
@app.route('/get-transaction', methods=['POST'])
@auth.login_required
def get_transaction():
    trans_id = request.form.get('trans_id')
    transaction = connectors.finam.get_page_transaction(trans_id)
    return transaction.json()


@logger.catch
@app.route('/get-short-stat', methods=['POST'])
@auth.login_required
def get_short_stat():
    transaction = connectors.finam.get_get_short_stat()
    return transaction.json()


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
@app.route('/dribbble-liker', methods=['GET', 'POST'])
@auth.login_required
def like_dribbble():
    if request.method == 'POST':
        acc_target = request.form.get('acc_target')
        add_link = request.form.get('add_link')
        add_quantity = request.form.get('add_quantity')
        rm = request.form.get('rm')
        form_dict = request.form.to_dict()
        if acc_target:
            try:
                acc_target = int(acc_target)
            except ValueError:
                flash('Use numbers, jerk!')
            else:
                if acc_target >= 0:
                    connectors.drbl_like.set_need_accs(int(acc_target))
                else:
                    flash('Only positive numbers')
        elif add_link and add_quantity:
            try:
                add_quantity = int(add_quantity)
            except ValueError:
                flash('Use numbers, jerk!')
            else:
                if add_quantity < 1:
                    flash('Only positive numbers')
                else:
                    if is_dribbble_link(add_link):
                        connectors.drbl_like.set_new_task(add_link, add_quantity)
                    else:
                        flash("It isn't right url")
        elif rm and rm.isdigit():
            rm_id = int(rm)
            connectors.drbl_like.rm_task(rm_id)
        elif form_dict:
            key_add = list(filter(lambda x: x.split(':')[0] == 'add', form_dict.keys()))[0]
            id_task = int(key_add.split(':')[-1])
            try:
                num = int(form_dict[key_add])
            except ValueError:
                flash('Use numbers, jerk!')
            else:
                connectors.drbl_like.add_likes(id_task, num)

    return render_template(
        'drbl_like.html',
        pagedata=connectors.drbl_like.get_page_data()
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


@logger.catch
@app.route('/get_categories', methods=['POST'])
def get_categories():
    flat_cat = tools.get_flat_cat(CATEGORIES)
    return json.dumps(flat_cat)
