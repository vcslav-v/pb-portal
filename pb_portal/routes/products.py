import calendar
import json
import os
from datetime import date, datetime, timedelta

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
@app_route.route('/list', methods=['GET', 'POST'])
@auth.login_required(role='admin')
def product_list():
    if request.method == 'POST':
        page_data = connectors.products.schemas.FilterPage()
        page_data.page = int(request.form.get('page'))

        if request.form.get(
            'end_design_date_datepicker_start'
        ) and request.form.get(
            'end_design_date_datepicker_end'
        ):
            page_data.end_design_date_start = date.fromisoformat(request.form.get(
                'end_design_date_datepicker_start'
            ))
            page_data.end_design_date_end = date.fromisoformat(request.form.get(
                'end_design_date_datepicker_end'
            ))

        if request.form.get('designer').isdecimal():
            page_data.designer_id = int(request.form.get('designer'))
        if request.form.get('category').isdecimal():
            page_data.category_id = int(request.form.get('category'))
        pbd = connectors.products.get_all(page_data)
        return render_template(
            '_product_page.html',
            pbd=pbd,
            products_img_url=connectors.products.PRODUCTS_IMG_URL,
        )
    else:
        page_data = connectors.products.get_page_data()
        return render_template(
            'product_base.html',
            page_data=page_data
        )


def get_form_list(form_data: dict, key_word: str):
    result = []
    for key in form_data:
        if len(key.split('|')[0]) > 1 and key.split('|')[0] == key_word:
            if form_data[key] == 'on':
                result.append(key.split('|')[-1])
    return result


@logger.catch
@app_route.route('/uploader', methods=['GET', 'POST'])
@auth.login_required(role=['admin', 'pb_admin'])
def uploader():
    # TODO research https://www.plupload.com/
    if request.method == 'POST':
        product_schema = connectors.products.schemas.UploadProduct(
            prefix=request.form.get('prefix'),
            product_file_name=request.form.get('product_file_name'),
            title=request.form.get('title'),
            slug=request.form.get('slug'),
            size=f'{request.form.get("product_size_mb")} mb',
            excerpt=request.form.get('excerpt'),
            description=request.form.get('description'),
            categories=get_form_list(request.form.to_dict(), 'category'),
            formats=get_form_list(request.form.to_dict(), 'format'),
            date_upload=datetime.strptime(request.form.get('date'), '%d-%m-%Y %H:%M') - timedelta(hours=3) if request.form.get('date') else datetime.utcnow(),
            tags=list(set([tag.strip() for tag in request.form.get('tags').split(', ') if tag.strip()]))
        )
        if request.form.get('schedule_date'):
            product_schema.schedule_date = datetime.strptime(request.form.get('schedule_date'), '%d-%m-%Y %H:%M') - timedelta(hours=3)
        if request.form.get('guest_author') and request.form.get('guest_author_link'):
            product_schema.guest_author = request.form.get('guest_author')
            product_schema.guest_author_link = request.form.get('guest_author_link')
        if request.form.get('product_type') == 'Freebie':
            freebie_schema = connectors.products.schemas.UploadFreebie.parse_obj(product_schema)
            freebie_schema.download_by_email = True if request.form.get('download_by_email') else False
            connectors.products.upload_freebie(freebie_schema)
        elif request.form.get('product_type') == 'Plus':
            plus_schema = connectors.products.schemas.UploadPlus.parse_obj(product_schema)
            connectors.products.upload_plus(plus_schema)
        elif request.form.get('product_type') == 'Premium':
            prem_schema = connectors.products.schemas.UploadPrem.parse_obj(product_schema)
            prem_schema.standart_price = int(request.form.get('standart_price'))
            prem_schema.extended_price = int(request.form.get('extended_price'))
            if request.form.get('sale_standart_price'):
                prem_schema.sale_standart_price = int(request.form.get('sale_standart_price'))
            if request.form.get('sale_extended_price'):
                prem_schema.sale_extended_price = int(request.form.get('sale_extended_price'))
            prem_schema.compatibilities = get_form_list(request.form.to_dict(), 'compatibility')
            connectors.products.upload_prem(prem_schema)

        return json.dumps({'prefix': request.form.get('prefix')})
    upload_page_info = connectors.products.get_upload_page_data()
    return render_template(
            'drag_drop.html',
            upload_page_info=upload_page_info,
        )


@logger.catch
@app_route.route('/product_schedule', methods=['GET', 'POST'])
@auth.login_required(role=['admin', 'pb_admin'])
def product_schedule():
    products = connectors.products.get_schedule_page()
    for product in products.page:
        product.date_time = product.date_time + timedelta(hours=3)
    return render_template(
            'product_schedule.html',
            products=products,
        )


@logger.catch
@app_route.route('/prepare_s3_url', methods=['GET'])
def prepare_s3_url():
    filename = request.args.get('filename')
    cur_filename = request.args.get('cur_filename')
    right_filename = f'{filename}.{cur_filename.split(".")[-1]}'
    content_type = 'application/octet-stream'
    prefix = request.args.get('prefix')
    try:
        result = connectors.products.make_s3_url(
            right_filename,
            content_type,
            prefix,
        )
    except Exception as e:
        logger.error(e.args)
        return
    return result


@logger.catch
@app_route.route('/get_upload_status', methods=['POST'])
def get_upload_status():
    prefix = request.form.get('prefix')
    result = {'status': connectors.products.get_upload_status(prefix)}
    return json.dumps(result)


@logger.catch
@app_route.route('/get_correct_slug', methods=['POST'])
def get_correct_slug():
    slug = request.form.get('slug')
    product_type = request.form.get('product_type').lower()
    result = connectors.products.get_correct_slug(slug, product_type)
    return json.dumps(result)


@logger.catch
@app_route.route('/rm_task', methods=['POST'])
def rm_task():
    ident = request.form.get('ident')
    connectors.products.rm_task(int(ident))
    return '{}'


@logger.catch
@app_route.route('/edit_task', methods=['POST'])
def edit_task():
    ident = request.form.get('ident')
    update = connectors.products.schemas.ScheduleUpdate(
        date_time=datetime.strptime(request.form.get('date_time'), '%d-%m-%Y %H:%M') - timedelta(hours=3)
    )
    connectors.products.update_task(int(ident), update)
    return '{}'
