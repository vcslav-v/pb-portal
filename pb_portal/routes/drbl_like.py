import os
from urllib.parse import urlparse

from flask import Blueprint, flash, render_template, request
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from pb_portal import connectors
from werkzeug.security import check_password_hash, generate_password_hash

app_route = Blueprint('route', __name__, url_prefix='/dribbble-liker')

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


def is_dribbble_link(uri):
    try:
        result = urlparse(uri)
        return result.netloc == 'dribbble.com'
    except AttributeError:
        return False
