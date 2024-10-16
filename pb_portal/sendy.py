from pb_portal import config
import requests


def add_unsubscribe_list(email: str):
    data = {
        'api_key': config.SENDY_API_KEY,
        'email': email,
        'list': config.UNSUBSCRIBERS_LIST_ID,
    }
    requests.post(
        config.SENDY_API_URL.format(action='subscribe'),
        data=data
    )
