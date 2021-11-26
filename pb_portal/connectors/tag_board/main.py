import os

import requests
from pb_portal.connectors.tag_board import schemas

NETLOC = os.environ.get('TAG_BOARD_NETLOC')
TOKEN = os.environ.get('TAG_BOARD_TOKEN')


def get_items_by_title(title) -> schemas.SearchResult:
    resp = requests.get(f'https://{NETLOC}/api/items-by-title/{title}?token={TOKEN}')
    if resp.ok:
        return schemas.SearchResult.parse_raw(resp.content)
    return schemas.SearchResult(
        items=[],
        tags_stat=[],
    )


def get_items_by_tag(tag) -> schemas.SearchResult:
    resp = requests.get(f'https://{NETLOC}/api/items-by-tag/{tag}?token={TOKEN}')
    if resp.ok:
        return schemas.SearchResult.parse_raw(resp.content)
    return schemas.SearchResult(
        items=[],
        tags_stat=[],
    )


def push_xlsx(file_data) -> bool:
    files = {'file_data': (file_data.filename, file_data.stream, file_data.content_type)}
    resp = requests.post(
        f'https://{NETLOC}/api/items_xls?token={TOKEN}',
        files=files,
    )
    if resp.ok:
        return True
    return False
