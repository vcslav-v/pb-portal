import os
from datetime import datetime
from random import randint

from flask import Blueprint, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from pb_portal import connectors, mem
import json

STORAGE_URL = os.environ.get('STORAGE_URL', '')
STATIC_URL = os.environ.get('STATIC_URL', 'http://127.0.0.1:5002')

app_route = Blueprint('route', __name__, url_prefix='/mail')

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
@app_route.route('/digest', methods=['GET', 'POST'])
@auth.login_required(role=['admin', 'pb_admin'])
def digest():
    ident = str(int(datetime.utcnow().timestamp())) + str(randint(0, int(datetime.utcnow().timestamp())))
    if request.method == 'POST':
        select_type = request.form.get('select_type')
        if select_type == 'premium_big':
            return render_template(
                '_digest_field_big_prem.html',
                ident=ident,
            )
        elif select_type == 'common_big':
            return render_template(
                '_digest_field_big_common.html',
                ident=ident,
            )
        elif select_type == 'product_grid':
            return render_template(
                '_digest_field_grid.html',
                ident=ident,
            )
        elif select_type == 'product_grid_row':
            return render_template(
                '_digest_field_grid_row.html',
                ident=ident,
            )
        elif select_type == 'bee_free':
            return render_template(
                '_digest_field_bee_free.html',
                ident=ident,
            )

    return render_template(
        'digest.html',
        base_url=STATIC_URL,
    )


@logger.catch
@app_route.route('/featured_source', methods=['GET', 'POST'])
@auth.login_required(role=['admin', 'pb_admin'])
def featured_source():
    if request.method == 'POST':
        if request.form.get('first_try') == 'true':
            data = connectors.mailer.schemas.PbFeatured(**request.form.to_dict())
        else:
            gallery_rows = []
            if request.form.get('gallery_rows'):
                for gallery_row in json.loads(request.form.get('gallery_rows')):
                    if not gallery_row.get('left_img_num') or not gallery_row.get('right_img_num') or not gallery_row.get('left_img_num').isdigit() or not gallery_row.get('right_img_num').isdigit():
                        continue
                    gallery_rows.append(
                        connectors.mailer.schemas.GalleryRow(
                            left_img_num=int(gallery_row.get('left_img_num')),
                            right_img_num=int(gallery_row.get('right_img_num')),
                        )
                    )

            data = connectors.mailer.schemas.PbFeatured(
                product_url=request.form.get('product_url'),
                first_try=request.form.get('first_try'),
                num_cover_img=request.form.get('num_cover_img'),
                main_gallery_img_num=request.form.get('main_gallery_img_num'),
                last_gallery_img_num=request.form.get('last_gallery_img_num'),
                gallery_rows=gallery_rows,
                exerpt=request.form.get('exerpt'),
                label=request.form.get('label'),
                description=request.form.get('description'),
                details=json.loads(request.form.get('details')) if request.form.get('details') else [],
                video=connectors.mailer.schemas.Video.parse_raw(request.form.get('video')) if request.form.get('video') else None,
                bundle=connectors.mailer.schemas.Bundle.parse_raw(request.form.get('bundle')) if request.form.get('bundle') else None,
                popular=json.loads(request.form.get('popular')) if request.form.get('popular') else [],
                campaign_name=request.form.get('campaign_name'),
            )
        result = connectors.mailer.make_featured(data)
        page_ident = str(
            int(datetime.utcnow().timestamp()) + randint(0, int(datetime.utcnow().timestamp()))
        )
        mem.set_digest(
            page_ident,
            result.html,
        )
        result.preview_url = f'{url_for("mail.show_digest")}?ident={page_ident}'
        return connectors.mailer.schemas.PbFeaturedPage(
            data=result,
            controls=render_template('_featured_control.html', result=result)
        ).json()
    return render_template(
        'featured_source.html',
        base_url=STATIC_URL,
    )


@logger.catch
@app_route.route('/get_featured_gallery_row', methods=['POST'])
def get_featured_gallery_row():
    return render_template(
        '_featured_gallery_row.html',
    )


@logger.catch
@app_route.route('/get_featured_detail_row', methods=['POST'])
def get_featured_detail_row():
    return render_template(
        '_featured_detail.html',
    )


@logger.catch
@app_route.route('/get_featured_video', methods=['POST'])
def get_featured_video():
    return render_template(
        '_featured_video.html',
    )


@logger.catch
@app_route.route('/get_featured_bundle', methods=['POST'])
def get_featured_bundle():
    return render_template(
        '_featured_bundle.html',
    )


@logger.catch
@app_route.route('/get_featured_bundle_row', methods=['POST'])
def get_featured_bundle_row():
    return render_template(
        '_featured_bundle_row.html',
    )


@logger.catch
@app_route.route('/get_featured_similar', methods=['POST'])
def get_featured_similar():
    return render_template(
        '_featured_similar.html',
    )


@logger.catch
@app_route.route('/make_digest', methods=['POST'])
@auth.login_required(role=['admin', 'pb_admin'])
def make_digest():
    data = request.form.to_dict()
    data.pop('campaign_name')
    data = connectors.mailer.schemas.PbDigest(data=data, campaign_name=request.form.get('campaign_name'))
    result = connectors.mailer.make_digest(data)
    page_ident = str(
        int(datetime.utcnow().timestamp()) + randint(0, int(datetime.utcnow().timestamp()))
        )
    mem.set_digest(
        page_ident,
        result,
    )
    return f'{url_for("mail.show_digest")}?ident={page_ident}'


@logger.catch
@app_route.route('/show_digest', methods=['GET'])
@auth.login_required(role=['admin', 'pb_admin'])
def show_digest():
    return mem.get_digest(request.args.get('ident'))
