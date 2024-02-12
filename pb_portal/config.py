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
