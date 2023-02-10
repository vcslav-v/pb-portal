import os

import requests
from pb_portal.connectors.products import schemas
from pb_portal.connectors import pb
from boto3 import session as s3_session
from loguru import logger
import json

API_URL = os.environ.get('PRODUCTS_URL', '')
TOKEN = os.environ.get('PRODUCTS_TOKEN', '')
DO_SPACE_REGION = os.environ.get('DO_SPACE_REGION', '')
DO_SPACE_ENDPOINT = os.environ.get('DO_SPACE_ENDPOINT', '')
DO_SPACE_KEY = os.environ.get('DO_SPACE_KEY', '')
DO_SPACE_SECRET = os.environ.get('DO_SPACE_SECRET', '')
DO_SPACE_BUCKET = os.environ.get('DO_SPACE_BUCKET', '')

POSIBLE_CATS = [
    'Add-Ons',
    'Brush Packs',
    'Effects',
    'Fonts',
    'Graphics',
    'HTML',
    'Icons',
    'Logo Templates',
    'Patterns',
    'photo',
    'Presentations',
    'PS Actions',
    'PSD Mockups',
    'Social Media',
    'templates',
    'Textures',
    'UI/UX Resources',
    'Vectors',
]

POSIBLE_FORMATS = [
    'ABR',
    'AFBRUSHES',
    'AI',
    'ASL',
    'ATN',
    'BRUSH',
    'BRUSHSET',
    'CDR',
    'EOT',
    'EPS',
    'FIG',
    'GIF',
    'GRD',
    'HTML',
    'JPG',
    'Lightroom',
    'OTF',
    'TTF',
    'WOFF',
    'Webfonts',
    'PAT',
    'PDF',
    'PNG',
    'PROCREATE',
    'PSD',
    'SVG',
    'SWATCHES',
    'TIFF',
    'TXT',
    'XD',
]


def get_all(page_data: schemas.FilterPage) -> schemas.ProductPage:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'{API_URL}/api/products', data=page_data.json())
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
        session.post(f'{API_URL}/api/pb_freebie_upload', data=freebie.json())


@logger.catch()
def get_upload_page_data() -> schemas.UploadProductPageInfo:
    result = schemas.UploadProductPageInfo(
        categories=pb.get_site_info_of('category', POSIBLE_CATS),
        formats=pb.get_site_info_of('format', POSIBLE_FORMATS),
        compatibilities=pb.get_site_info_of('compatibility'),
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