from bs4 import BeautifulSoup
from pb_portal import config
import re
from pb_portal.schemas.new_product import UploadForm
from starlette.datastructures import FormData

def description(html_text: str) -> tuple[int, list[str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    tags = {tag.name for tag in soup.find_all()}
    forbidden_tags = tags - config.ALLOWED_TAGS
    plain_text = soup.get_text()
    return len(plain_text.strip()), forbidden_tags


def exerpt(text: str) -> tuple[int, str]:
    if not text:
        return 0, ''
    text_line = '' if re.match(config.RE_EXERPT, text) else 'Only letters, numbers, ampersands, hyphens, commas and periods are allowed' # noqa
    return len(text), text_line


def tags(tags_str: str) -> tuple[list[str], str]:

    tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
    validated_tags = [tag for tag in tags if re.match(config.RE_TAG, tag)]
    text_line = 'Please enter only letters, numbers, spaces, and hyphens are allowed' if len(validated_tags) != len(tags) else '' # noqa
    return validated_tags, text_line


def youtube_thumbnail(url: str) -> str:
    for res in config.YOUTUBE_RES:
        match = re.search(res, url)
        if match:
            return f'https://img.youtube.com/vi/{match.group(1)}/hqdefault.jpg'
    return ''


def upload_form(upload_session: UploadForm, form: FormData, html_text: str) -> bool:
    # title
    is_valid = re.match(config.RE_TITLE, form.get('title', '')) and len(form.get('title', '')) <= config.MAX_LENGHT_TITLE
    # product file
    upload_session.errors.file_upload = not form.get('productName', False)
    is_valid = is_valid and not upload_session.errors.file_upload
    # formats
    upload_session.errors.formats = len(form.getlist('formats[]')) == 0
    is_valid = is_valid and (
        all(
            format in config.SUPPORTED_FORMATS for format in form.getlist('formats[]')
        ) and not upload_session.errors.formats
    )
    # excerpt
    is_valid = is_valid and re.match(
        config.RE_EXERPT, form.get('excerpt', '')
    ) and len(form.get('excerpt', '')) <= config.MAX_EXERPT_LENGTH
    # description
    length, forb_tags = description(html_text)
    upload_session.errors.desc = length == 0
    is_valid = is_valid and not upload_session.errors.desc and not forb_tags
    # tags
    is_valid = is_valid and 0 < len(form.get('tags', '').split(',')) <= config.MAX_TAGS_LENGTH
    # previews
    for preview in upload_session.previews:
        config.logger.info('youtube' not in preview.thumb_url and str(preview.id) in form.getlist('preview_ids[]'))
        config.logger.info(preview.id)
        config.logger.info(form.getlist('preview_ids[]'))
        if 'youtube' not in preview.thumb_url and str(preview.id) in form.getlist('preview_ids[]'):
            upload_session.errors.previews = False
            break
    else:
        upload_session.errors.previews = True
        is_valid = False

    return is_valid
