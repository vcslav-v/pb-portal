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
    result = r.get(config.REDIS_SENDY_UNSUB_TEMPLATE.format(email=email))
    if not result:
        return False
    r.delete(config.REDIS_SENDY_UNSUB_TEMPLATE.format(email=email))
    return True
