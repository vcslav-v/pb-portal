from pb_portal import config, mem
import requests


def add_unsubscribe_list(email: str):
    data = {
        'api_key': config.SENDY_API_KEY,
        'email': email,
        'list': config.AUTO_UNSUBSCRIBERS_LIST_ID if mem.is_auto_unsubscribed_sendy_pop(email) else config.UNSUBSCRIBERS_LIST_ID, # noqa
    }
    requests.post(
        config.SENDY_API_URL.format(action='subscribe'),
        data=data
    )


def rm_unsubscribe_list(email: str):
    data = {
        'api_key': config.SENDY_API_KEY,
        'list_id': config.UNSUBSCRIBERS_LIST_ID,
        'email': email,
    }
    requests.post(
        config.SENDY_API_URL.format(action='api/subscribers/delete.php'),
        data=data
    )
    data = {
        'api_key': config.SENDY_API_KEY,
        'list_id': config.AUTO_UNSUBSCRIBERS_LIST_ID,
        'email': email,
    }
    requests.post(
        config.SENDY_API_URL.format(action='api/subscribers/delete.php'),
        data=data
    )
