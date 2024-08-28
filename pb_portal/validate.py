from bs4 import BeautifulSoup
from pb_portal import config
import re


def description(html_text: str) -> tuple[int, list[str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    tags = {tag.name for tag in soup.find_all()}
    forbidden_tags = tags - config.ALLOWED_TAGS
    plain_text = soup.get_text()
    return len(plain_text), forbidden_tags


def exerpt(text: str) -> tuple[int, str]:
    if not text:
        return 0, ''
    text_line = '' if re.match(config.RE_EXERPT, text) else 'Only letters, numbers, spaces, and hyphens are allowed'
    return len(text), text_line


def tags(tags_str: str) -> tuple[list[str], str]:

    tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
    validated_tags = [tag for tag in tags if re.match(config.RE_TAG, tag)]
    text_line = 'Only letters, numbers, spaces, and hyphens are allowed' if len(validated_tags) != len(tags) else ''
    return validated_tags, text_line
