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

SAMPLE_PRODUCT_URL = os.environ.get('SAMPLE_PRODUCT_URL', 'https://www.google.com')
SUPPORTED_FORMATS = os.environ.get('SUPPORTED_FORMATS', 'pdf,doc,docx,txt').split(',')

ALLOWED_TAGS = {
    'p', 'i', 'b', 'strong', 'em', 'u', 'strike', 'ol', 'ul', 'li', 'br'
}
MAX_DESCRIPTION_LENGTH = 1000
MAX_EXERPT_LENGTH = 250
RE_EXERPT = r'^[\w+\' \-()]+$'
MAX_TAGS_LENGTH = 20
RE_TAG = r'^[a-z0-9\' -]+$'

# DigitalOcean Spaces
DO_SPACE_KEY = os.environ.get('DO_SPACE_KEY', '')
DO_SPACE_SECRET = os.environ.get('DO_SPACE_SECRET', '')
DO_SPACE_REGION = os.environ.get('DO_SPACE_REGION', '')
DO_SPACE_BUCKET = os.environ.get('DO_SPACE_BUCKET', '')
DO_SPACE_ENDPOINT = os.environ.get('DO_SPACE_ENDPOINT', '')

