import os

import requests
from pb_portal.connectors.drbl_like import schemas

NETLOC = os.environ.get('DRBL_BOT_NETLOC') or ''
TOKEN = os.environ.get('DRBL_BOT_TOKEN') or ''


def get_page_data() -> schemas.LikerPage:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/get-liker-page')
        if resp.ok:
            return schemas.LikerPage.parse_raw(resp.content)
        return schemas.LikerPage()


def set_new_task(link: str, quantity: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'https://{NETLOC}/api/add-task?link={link}&quantity={quantity}')
        resp.raise_for_status


def set_need_accs(acc_target: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'https://{NETLOC}/api/target-acc?acc_target={acc_target}')
        resp.raise_for_status


def rm_task(task_id: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(f'https://{NETLOC}/api/rm-task?task_id={task_id}')
        resp.raise_for_status


def add_likes(task_id: int, num_likes: int):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.post(
            f'https://{NETLOC}/api/add-task-likes?task_id={task_id}&num_likes={num_likes}'
        )
        resp.raise_for_status
