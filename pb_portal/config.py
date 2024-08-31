import os
import sys
from dotenv import load_dotenv
from loguru import logger

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    logger.remove()
    logger.add(sys.stderr, level='DEBUG')
    IS_DEV = True
    load_dotenv(dotenv_path)
    logger.info('Loaded .env file')
else:
    logger.remove()
    logger.add(sys.stderr, level='INFO')
    IS_DEV = False

# FastAPI
API_USERNAME = os.environ.get('API_USERNAME', 'api')
API_PASSWORD = os.environ.get('API_PASSWORD', 'pass')
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

# Auth
AUTH_SECRET = os.environ.get('AUTH_SECRET', 'auth_secret')
USER_MANAGER_SECRET = os.environ.get('USER_MANAGER_SECRET', 'user_manager_secret')


# Database
DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql+asyncpg://postgres:mysecretpassword@0.0.0.0/postgres')

# PB
PB_URL = os.environ.get('PB_URL', '')
PB_LOGIN = os.environ.get('PB_LOGIN', 'login')
PB_PASSWORD = os.environ.get('PB_PASSWORD', 'password')
PB_CALLBACK_URL = os.environ.get('PB_CALLBACK_URL', 'https://example.com/callback/{product_id}')
PB_UPL_API_LOGIN = os.environ.get('PB_UPL_API_LOGIN', '')
PB_UPL_API_PASS = os.environ.get('PB_UPL_API_PASS', '')
PB_UPL_API_URL = os.environ.get('PB_UPL_API_URL', '')
PB_BASIC_LOGIN = os.environ.get('PB_BASIC_LOGIN', '')
PB_BASIC_PASSWORD = os.environ.get('PB_BASIC_PASSWORD', '')

SAMPLE_PRODUCT_URL = os.environ.get('SAMPLE_PRODUCT_URL', 'https://www.google.com')
SUPPORTED_FORMATS = os.environ.get('SUPPORTED_FORMATS', 'pdf,doc,docx,txt').split(',')
PUBLISH_INTERVAL = int(os.environ.get('PUBLISH_INTERVAL', 30))

ALLOWED_TAGS = {
    'p', 'i', 'b', 'strong', 'em', 'u', 'strike', 'ol', 'ul', 'li', 'br'
}
MAX_DESCRIPTION_LENGTH = 1000
MAX_EXERPT_LENGTH = 250
RE_EXERPT = r'^[a-zA-Z0-9\' \&\-()\.,]+$'
MAX_TAGS_LENGTH = 20
RE_TAG = r'^[a-zA-Z0-9\'\& -]+$'
RE_TITLE = r'^[a-zA-Z][a-zA-Z0-9& \-]*$'
MAX_LENGHT_TITLE = 50

# Images
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MIN_PB_IMAGE_WIDTH = 2250
MIN_PB_IMAGE_HEIGHT = 1500
PB_IMAGE_ASPECT_RATIO = 3 / 2
MAX_IMAGE_WIDTH = 3000
MAX_IMAGE_HEIGHT = 2000
PORTAL_PREVIEW_IMAGE_WIDTH = 500
PORTAL_PREVIEW_IMAGE_HEIGHT = 500
THUMBNAIL_WIDTH = 640
THUMBNAIL_HEIGHT = 426
PUSH_IMAGE_WIDTH = 400
PUSH_IMAGE_HEIGHT = 400

YOUTUBE_RES = [
    r'v=([a-zA-Z0-9_-]{11})',
    r'youtu\.be/([a-zA-Z0-9_-]{11})',
]


# DigitalOcean Spaces
DO_SPACE_KEY = os.environ.get('DO_SPACE_KEY', '')
DO_SPACE_SECRET = os.environ.get('DO_SPACE_SECRET', '')
DO_SPACE_REGION = os.environ.get('DO_SPACE_REGION', '')
DO_SPACE_BUCKET = os.environ.get('DO_SPACE_BUCKET', '')
DO_SPACE_ENDPOINT = os.environ.get('DO_SPACE_ENDPOINT', '')

IMG_S3_NAME_TEMPLATE = 'uploaded_products/{upload_session_id}/preview_{filename}_{img_id}_{target}.jpg'
YOUTUBE_S3_NAME_TEMPLATE = 'uploaded_products/{upload_session_id}/preview_{img_id}_youtube.txt'
PRODUCT_S3_NAME_TEMPLATE = 'uploaded_products/{upload_session_id}/product.zip'
UPLOADED_PRODUCTS_DIR = 'uploaded_products/{upload_session_id}/'
