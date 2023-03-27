import os
from urllib.parse import urlparse

import redis

DIGEST_PREFIX = 'DIGEST|'

REDIS = os.environ.get('REDIS_TLS_URL')
if REDIS:
    parsed_redis_url = urlparse(REDIS)
    r = redis.Redis(
        host=parsed_redis_url.hostname,
        port=parsed_redis_url.port,
        username=parsed_redis_url.username,
        password=parsed_redis_url.password,
        ssl=True,
        ssl_cert_reqs=None,
        decode_responses=True,
    )
else:
    r = redis.Redis(
        host=os.environ.get('REDIS') or 'localhost',
        decode_responses=True,
    )


def set_digest(ident, value):
    r.set(f'DIGEST_PREFIX{ident}', value)


def get_digest(ident):
    return r.get(f'DIGEST_PREFIX{ident}')


def flush_all():
    r.flushall()
