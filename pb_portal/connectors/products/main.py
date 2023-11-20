import os

import requests
from pb_portal.connectors.products import schemas
from pb_portal.connectors import pb
from boto3 import session as s3_session
from loguru import logger
import json
from pb_admin import schemas as pb_schemas

API_URL = os.environ.get('PRODUCTS_URL', '')
TOKEN = os.environ.get('PRODUCTS_TOKEN', '')
DO_SPACE_REGION = os.environ.get('DO_SPACE_REGION', '')
DO_SPACE_ENDPOINT = os.environ.get('DO_SPACE_ENDPOINT', '')
DO_SPACE_KEY = os.environ.get('DO_SPACE_KEY', '')
DO_SPACE_SECRET = os.environ.get('DO_SPACE_SECRET', '')
DO_SPACE_BUCKET = os.environ.get('DO_SPACE_BUCKET', '')
PRODUCTS_IMG_URL = os.environ.get('PRODUCTS_IMG_URL', '')

FILTER_CATS = [
    'limited offer',
    'Articles',
    'sketch',
    'Interviews',
    'Sponsored',
    'html',
    'Selections',
    'Tutorials',
    'poster',
    'other',
    'animation'
]

FILTER_FORMATS = ['RTF', 'DOCX', 'IconJar', 'JPEG', 'PSD (vector based logos)', 'VFB', 'DOC', 'SVG. PNG', 'JS', 'OTF & TTF', 'idml', 'PSD (vector-based logos)', 'AEP', 'GLIF', 'WOOF', 'SVG and PNG', 'OTF. TTF', 'AIA', 'KEY', 'SKETCH', 'ACV', 'XMP', 'LRTEMPLATE', 'PPTX', 'JPG (3000x3000px)', 'INDD', 'Lightroom Template', 'PPT', 'EPS. PNG', 'WOFF2', 'CSH', 'PSB', 'PSD (5616x3744px)', 'InDesign', 'MS Word', 'CSS', 'OTF. WOFF', 'TIF']
FILTER_TAGS = []


def get_all(page_data: schemas.FilterPage) -> schemas.ProductPage:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/products', data=page_data.model_dump())
        logger.debug(resp.content)
        if resp.ok:
            return schemas.ProductPage.parse_raw(resp.content)
        return schemas.ProductPage()


def get_page_data() -> schemas.ProductPageData:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{API_URL}/api/common_data')
        logger.debug(resp.content)
        if resp.ok:
            return schemas.ProductPageData.parse_raw(resp.content)
        return schemas.ProductPageData()


def upload_freebie(freebie: schemas.UploadFreebie):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        session.post(f'{API_URL}/api/pb_freebie_upload', json=freebie.model_dump())


def upload_plus(plus: schemas.UploadPlus):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        session.post(f'{API_URL}/api/pb_plus_upload', json=plus.model_dump())


def upload_prem(prem: schemas.UploadPrem):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/pb_prem_upload', json=prem.model_dump())
        logger.debug(resp.content)


@logger.catch()
def get_upload_page_data() -> schemas.UploadProductPageInfo:
    result = schemas.UploadProductPageInfo(
        categories=pb.get_site_info_of('category', FILTER_CATS),
        formats=pb.get_site_info_of('format', FILTER_FORMATS),
        compatibilities=pb.get_site_info_of('compatibility'),
        tags=pb.get_site_info_of_tags(FILTER_TAGS),
    )
    return result


@logger.catch
def make_s3_url(filename, content_type, prefix):
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=DO_SPACE_REGION,
            endpoint_url=DO_SPACE_ENDPOINT,
            aws_access_key_id=DO_SPACE_KEY,
            aws_secret_access_key=DO_SPACE_SECRET
        )

    presigned_post = client.generate_presigned_post(
        Bucket=DO_SPACE_BUCKET,
        Key=f'temp/{prefix}/{filename}',
        Fields={"acl": "public-read", "Content-Type": content_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": content_type}
        ],
        ExpiresIn=3600,
    )
    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (DO_SPACE_BUCKET, f'temp/{prefix}/{filename}')
    })


@logger.catch
def get_upload_status(prefix):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/get_status_upload?prefix={prefix}')
        if resp.ok:
            return resp.text.strip('"')
        return 'Error'


@logger.catch
def get_correct_slug(slug: str, product_type: str):
    if not pb.get_correct_slug(slug, product_type).get('is_exists'):
        return {'slug': slug}
    i = 0
    while pb.get_correct_slug(f'{slug}-{i}', product_type).get('is_exists') and i < 10:
        i += 1
    return {'slug': f'{slug}-{i}'}


@logger.catch
def get_schedule_page():
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/get_product_schedule')
        resp.raise_for_status()
        return schemas.PageProductsSchedule.parse_raw(resp.content)


@logger.catch
def rm_task(ident: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/rm_task/{ident}')
        resp.raise_for_status()


@logger.catch
def update_task(ident: int, update: schemas.ScheduleUpdate):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/update_date_task/{ident}', json=update.model_dump())
        resp.raise_for_status()


@logger.catch
def set_bulk_tag(products: list[pb_schemas.Product], tag: str, category_id: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        data = schemas.BulkTag(tag=tag, products=[], category_id=category_id)
        data.products = products
        resp = session.post(f'{API_URL}/api/set_bulk_tag', json=data.model_dump())
        resp.raise_for_status()


@logger.catch
def count_active_bulk_task():
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{API_URL}/api/bulk_tag_count_tasks')
        resp.raise_for_status()
        return resp.text
