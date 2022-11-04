import os

import requests
from loguru import logger
import io

NETLOC = os.environ.get('GRAPH_NETLOC') or '127.0.0.1:8000'
TOKEN = os.environ.get('GRAPH_TOKEN') or 'pass'


@logger.catch
def get_tiny_zip(files_data, resize_width=None):
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        files = []
        for file_data in files_data:
            files.append(
                ('files', (file_data.filename, file_data.stream, file_data.content_type))
            )
        url = f'https://{NETLOC}/api/tinify'
        url = url + f'?width={resize_width}' if resize_width else url
        resp = session.post(
            url,
            files=files,
        )
        resp.raise_for_status()
        zip_file = io.BytesIO(resp.content)
        return zip_file


@logger.catch
def get_long_jpg(files_data, raw_width: str, raw_height: str, raw_n_cols: str):
    if raw_width and raw_height:
        if raw_width.isdigit() and raw_height.isdigit():
            width = int(raw_width)
            height = int(raw_height)
    else:
        width = -1
        height = -1
    if raw_n_cols and raw_n_cols.isdigit():
        n_cols = int(raw_n_cols)
    else:
        n_cols = 1

    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        files = []
        for file_data in files_data:
            files.append(
                ('files', (file_data.filename, file_data.stream, file_data.content_type))
            )
        url = f'https://{NETLOC}/api/long?wide={width}&high={height}&n_cols={n_cols}'
        resp = session.post(
            url,
            files=files,
        )
        resp.raise_for_status()
        long_jpg = io.BytesIO(resp.content)
        return long_jpg


@logger.catch
def get_gif(seq_prefix: str, frames_per_sec: int, files_data):
    frame_duration = 1000 // frames_per_sec if frames_per_sec else None
    with requests.sessions.Session() as session:
        session.auth = ('api', TOKEN)
        files = []
        for file_data in files_data:
            files.append(
                ('files', (file_data.filename, file_data.stream, file_data.content_type))
            )
        url = f'https://{NETLOC}/api/gif?prefix={seq_prefix}'
        url = url + f'&duration={frame_duration}' if frame_duration else url
        resp = session.post(
            url,
            files=files,
        )
        resp.raise_for_status()
        gif_file = io.BytesIO(resp.content)
        return gif_file
