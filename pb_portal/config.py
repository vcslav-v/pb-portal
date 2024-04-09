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
