from pb_admin import PbSession
from pb_portal import config
import os
import json


async def get_categories():
    config.logger.info('Getting categories')
    pb_session = PbSession(
        site_url=config.PB_URL,
        login=config.PB_LOGIN,
        password=config.PB_PASSWORD,
    )
    categories = pb_session.categories.get_list()
    categories.sort(key=lambda x: x.weight)
    categories = [category for category in categories if category.is_display]
    os.environ['PB_CATEGORIES'] = json.dumps(
        {category.ident: category.title for category in categories}
    )
