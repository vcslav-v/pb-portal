import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from datetime import datetime

from pb_portal import config

security = HTTPBasic()

username = config.API_USERNAME
password = config.API_PASSWORD


def get_templates():
    jinja_templates = Jinja2Templates(directory=config.TEMPLATES_DIR)
    jinja_templates.env.globals['_current_year'] = datetime.now().year
    return jinja_templates


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username
