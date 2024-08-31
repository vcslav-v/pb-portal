from pb_admin import PbSession, schemas as pb_schemas
from pb_admin.schemas import NewProduct
from pb_portal.db import models as db_models, tools as db_tools
from pb_portal import config, s3, imgs
from pb_portal.schemas.new_product import UploaderResponse, UploadForm
from pb_portal.auth import schemas as auth_schemas
import os
import json
from starlette.datastructures import FormData
import re
from datetime import datetime as dt, timezone as tz
import pytz
import requests
import math


def generate_slug(input_string):
    allowed_chars = re.sub(r'[^a-zA-Z0-9\s-]', '', input_string)
    slug = re.sub(r'[\s-]+', '_', allowed_chars)

    slug = slug.lower()
    return slug


async def get_categories():
    config.logger.info('Getting categories')
    pb_session = PbSession(
        site_url=config.PB_URL,
        login=config.PB_LOGIN,
        password=config.PB_PASSWORD,
        edit_mode=True
    )
    categories = pb_session.categories.get_list()
    categories.sort(key=lambda x: x.weight)
    categories = [category for category in categories if category.is_display]
    os.environ['PB_CATEGORIES'] = json.dumps(
        {category.ident: category.title for category in categories}
    )


async def get_creators():
    config.logger.info('Getting creators')
    pb_session = PbSession(
        site_url=config.PB_URL,
        login=config.PB_LOGIN,
        password=config.PB_PASSWORD,
        edit_mode=True
    )
    creators = pb_session.creators.get_list()
    creators.sort(key=lambda x: x.ident)
    os.environ['PB_CREATORS'] = json.dumps(
        {creator.ident: creator.name for creator in creators}
    )


def get_valid_tags_ids(pb_session: PbSession, tag_names: str) -> list[int]:
    tag_names = tag_names.split(',')
    tag_names = [tag_name.lower().strip() for tag_name in tag_names]
    result = []
    for tag_name in tag_names:
        pb_tags = pb_session.tags.get_list(search=tag_name)
        for pb_tag in pb_tags:
            if pb_tag.name.lower() == tag_name:
                tag_for_add = pb_session.tags.get(pb_tag.ident)
                break
        else:
            tag_for_add = pb_session.tags.fill_scheme_by_policy(
                 pb_schemas.Tag(
                     name=tag_name,
                 )
            )
            tag_for_add = pb_session.tags.create(tag_for_add)
        result.append(tag_for_add.ident)
    return result


async def upload_product(form: FormData, user: db_models.User, html_desc: str):
    config.logger.info('Uploading product')
    product_type = pb_schemas.NewProductType.freebie if form.get('productType') == 'free' else pb_schemas.NewProductType.plus
    title = form.get('title', '')
    slug = generate_slug(title)
    if form.get('schedule_date'):
        local_time = dt.strptime(form.get('schedule_date'), '%Y-%m-%d %H:%M')
        local_timezone = pytz.timezone(form.get('timezone', 'UTC'))
        localized_time = local_timezone.localize(local_time)
        utc_time = localized_time.astimezone(pytz.utc)
    else:
        utc_time = dt.now(tz.utc)
    presentation_urls = s3.presentation_files(form.get('upload_session_id', 'error'), form.getlist('preview_ids[]'))
    thumbnail, push_image, images, presentation = imgs.get_pb_graphics(
        presentation_urls,
        slug,
        title
    )
    size = s3.get_product_size(form.get('upload_session_id', 'error')) / 1024 / 1024
    if size < 1:
        size = '1 MB'
    elif size < 1000:
        size = f'{math.ceil(size)} MB'
    else:
        size = f'{size:.2f} GB'
    pb_session = PbSession(
        site_url=config.PB_URL,
        login=config.PB_LOGIN,
        password=config.PB_PASSWORD,
        edit_mode=True
    )
    new_product = NewProduct(
        product_type=product_type,
        created_at=utc_time,
        title=title,
        size=size,
        vps_path='unknown',
        s3_path='unknown',
        slug=slug,
        is_special=form.get('productType') == 'special',
        excerpt=form.get('excerpt', ''),
        description=html_desc,
        thumbnail=thumbnail,
        push_image=push_image,
        is_live=False,
        images=images,
        presentation=presentation,
        formats=', '.join(form.getlist('formats[]')),
        category_id=int(form.get('category')),
        creator_id=int(form.get('creator_id')) if user.role_id < auth_schemas.UserRoles.manager.value  else user.creator_id,
        price_commercial_cent=int(form.get('commercialPrice', 0))*100,
        price_extended_cent=int(form.get('extendedPrice', 0))*100 if form.get('extendedPrice') else None,
        price_commercial_sale_cent=None,
        price_extended_sale_cent=None,
        tags_ids=get_valid_tags_ids(pb_session, form.get('tags', '')),
        meta_title=f'Download {title}' if product_type == pb_schemas.NewProductType.freebie else title,
        meta_description=form.get('excerpt', ''),
    )
    pb_product = pb_session.new_products.create(new_product)
    product_file_url = s3.get_product_link(form.get('upload_session_id', 'error'), f'{pb_product.ident}_{slug}')
    if form.get('schedule_date'):
        await db_tools.add_schedule(pb_product.ident, utc_time)
    with requests.sessions.Session() as session:
        product = product_file_url.split('?')[0]
        data = {
            'upload': product,
            'type': 'freebie' if product_type == pb_schemas.NewProductType.freebie else 'plus',
            'load_to_s3': True,
            'callback': config.PB_CALLBACK_URL.format(product_id=pb_product.ident),
        }
        session.auth = (config.PB_UPL_API_LOGIN, config.PB_UPL_API_PASS)
        session.post(config.PB_UPL_API_URL, json=data)


def add_product_file(uploader_resp: UploaderResponse, product_id: int, in_schedule: bool = False):
    config.logger.info('Adding product file')
    pb_session = PbSession(
        site_url=config.PB_URL,
        login=config.PB_LOGIN,
        password=config.PB_PASSWORD,
        edit_mode=True
    )
    pb_product = pb_session.new_products.get(product_id)
    pb_product.vps_path = '/'.join(uploader_resp.local_link.split('/')[-2:])
    pb_product.s3_path = uploader_resp.s3_link.split('/')[-1]
    if not in_schedule:
        pb_product.is_live = True
    pb_session.new_products.update(pb_product)


def publish(product_ids: list[int]):
    config.logger.info('Publishing product')
    pb_session = PbSession(
        site_url=config.PB_URL,
        login=config.PB_LOGIN,
        password=config.PB_PASSWORD,
        edit_mode=True
    )
    for product_id in product_ids:
        pb_product = pb_session.new_products.get(product_id)
        pb_product.is_live = True
        pb_session.new_products.update(pb_product)
