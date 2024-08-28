from boto3 import session as s3_session
from pb_portal import config
import json


def make_s3_url(filename, content_type):
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )

    presigned_post = client.generate_presigned_post(
        Bucket=config.DO_SPACE_BUCKET,
        Key=f'uploaded_products/{filename}',
        Fields={"acl": "public-read", "Content-Type": content_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": content_type}
        ],
        ExpiresIn=3600,
    )
    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (config.DO_SPACE_BUCKET, f'uploaded_products/{filename}')
    })


def rm_product(filename):
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )
    client.delete_object(
        Bucket=config.DO_SPACE_BUCKET,
        Key=f'uploaded_products/{filename}'
    )
    return True
