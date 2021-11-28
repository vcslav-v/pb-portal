import os

import requests
from pb_portal.connectors.tag_board import schemas
from loguru import logger

NETLOC = os.environ.get('TAG_BOARD_NETLOC') or ''
TOKEN = os.environ.get('TAG_BOARD_TOKEN') or ''


def get_items_by_title(title) -> schemas.SearchResult:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/items-by-title/{title}')
        if resp.ok:
            logger.debug(resp.content)
            return schemas.SearchResult.parse_raw(resp.content)
        return schemas.SearchResult(
            items=[],
            tags_stat=[],
        )


def get_items_by_tag(tag) -> schemas.SearchResult:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        resp = session.get(f'https://{NETLOC}/api/items-by-tag/{tag}')
        if resp.ok:
            return schemas.SearchResult.parse_raw(resp.content)
        return schemas.SearchResult(
            items=[],
            tags_stat=[],
        )


def push_xlsx(file_data) -> bool:
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        files = {'file_data': (file_data.filename, file_data.stream, file_data.content_type)}
        resp = session.post(
            f'https://{NETLOC}/api/items_xls?token={TOKEN}',
            files=files,
        )
        if resp.ok:
            return True
        return False
