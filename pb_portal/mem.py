import redis
from pb_portal import config


def is_auto_unsubscribed_sendy_pop(email: str) -> bool:
    r = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        username=config.REDIS_USERNAME,
        password=config.REDIS_PASSWORD,
        ssl=True,
        ssl_cert_reqs=None,
        decode_responses=True,
    )
    result = r.get(f'sendy:{email}:is_auto_unsub')
    if not result:
        return False
    r.delete(f'sendy:{email}:is_auto_unsub')
    return True
