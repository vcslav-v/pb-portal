import os

import requests
from loguru import logger
from pb_portal.connectors.video import schemas

API_URL = os.environ.get('VIDEO_URL') or ''
TOKEN = os.environ.get('VIDEO_TOKEN') or ''


@logger.catch
def make_video_t1(zip_data_path, name):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        with open(zip_data_path, 'rb') as zip_file:
            files = {
                    'zip_file': zip_file,
                }
            url = f'{API_URL}/api/make-vt-1/{name}'
            resp = session.post(
                url,
                files=files,
            )
    resp.raise_for_status()


@logger.catch
def get_page() -> schemas.Page:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{API_URL}/api/page')
        resp.raise_for_status()
        return schemas.Page.parse_raw(resp.content)


@logger.catch
def get_link(uid: str) -> str:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'{API_URL}/api/link/{uid}')
        resp.raise_for_status()
        return resp.text.strip("'\"")


@logger.catch
def rm_video(uid: str):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.delete(f'{API_URL}/api/video/{uid}')
        resp.raise_for_status()