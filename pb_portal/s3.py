from boto3 import session as s3_session
from pb_portal import config
import json
import io
import os
import requests


def make_s3_url(upload_session_id, content_type):
    filename = config.PRODUCT_S3_NAME_TEMPLATE.format(
        upload_session_id=upload_session_id
    )
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
        Key=filename,
        Fields={"acl": "public-read", "Content-Type": content_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": content_type}
        ],
        ExpiresIn=3600,
    )
    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (config.DO_SPACE_BUCKET, filename)
    })


def rm_product(upload_session_id):
    filename = config.PRODUCT_S3_NAME_TEMPLATE.format(
        upload_session_id=upload_session_id
    )
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
        Key=filename
    )
    return True


def upload_pb_preview_image(
    imgs_data: list[tuple[io.BytesIO | None, io.BytesIO | None, str, str]],
    upload_session_id: str
) -> list[dict[str, str]]:
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )
    result = []
    for img_data in imgs_data:
        img_bytes, portal_bytes, error, filename = img_data
        if error:
            result.append({'error': error, 'filename': filename})
            continue
        img_bytes.seek(0)
        portal_bytes.seek(0)
        img_id = get_img_id(client, upload_session_id)
        img_filename = config.IMG_S3_NAME_TEMPLATE.format(
            upload_session_id=upload_session_id,
            target='for-pb-preview',
            img_id=img_id,
            filename=filename
        )
        portal_filename = config.IMG_S3_NAME_TEMPLATE.format(
            upload_session_id=upload_session_id,
            target='for-portal',
            img_id=img_id,
            filename=filename
        )
        client.upload_fileobj(
            img_bytes,
            config.DO_SPACE_BUCKET,
            img_filename,
            ExtraArgs={'ACL': 'public-read'}
        )
        client.upload_fileobj(
            portal_bytes,
            config.DO_SPACE_BUCKET,
            portal_filename,
            ExtraArgs={'ACL': 'public-read'}
        )
        result.append({
            'id': img_id,
            'thumb_url': get_s3_link(client, portal_filename),
            'filename': filename
        })
    return result


def rm_pb_preview(img_id: str, upload_session_id: str):
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )
    response = client.list_objects_v2(
        Bucket=config.DO_SPACE_BUCKET,
        Prefix=config.UPLOADED_PRODUCTS_DIR.format(upload_session_id=upload_session_id)
    )
    for content in response.get('Contents', []):
        if content['Key'].startswith(
            os.path.join(
                config.UPLOADED_PRODUCTS_DIR.format(upload_session_id=upload_session_id),
                'preview_'
            )
        ):
            do_img_id = content['Key'].split('_')[-2]
            if do_img_id == img_id:
                client.delete_object(
                    Bucket=config.DO_SPACE_BUCKET,
                    Key=content['Key']
                )
    return True


def get_img_id(client, upload_session_id):
    response = client.list_objects_v2(
        Bucket=config.DO_SPACE_BUCKET,
        Prefix=config.UPLOADED_PRODUCTS_DIR.format(upload_session_id=upload_session_id)
    )
    exist_img_ids = []
    for content in response.get('Contents', []):
        if content['Key'].startswith(
            os.path.join(
                config.UPLOADED_PRODUCTS_DIR.format(upload_session_id=upload_session_id),
                'preview_'
            )
        ):
            exist_img_ids.append(int(content['Key'].split('_')[-2]))
    return max(exist_img_ids) + 1 if exist_img_ids else 0


def get_s3_link(client, key: str):
    return client.generate_presigned_url(
        'get_object',
        Params={'Bucket': config.DO_SPACE_BUCKET, 'Key': key},
        ExpiresIn=24 * 60 * 60
    )


def make_youtube_placeholder(youtube_url, upload_session_id: str, thumbnail_url: str):
    if not thumbnail_url:
        return [{
            'error': 'Invalid youtube link',
            'filename': youtube_url if youtube_url else 'No link'
        }]
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )
    ident = get_img_id(client, upload_session_id)
    youtube_filename = config.YOUTUBE_S3_NAME_TEMPLATE.format(
        upload_session_id=upload_session_id,
        img_id=ident
    )
    client.upload_fileobj(
        io.BytesIO(youtube_url.encode('utf-8')),
        config.DO_SPACE_BUCKET,
        youtube_filename,
        ExtraArgs={'ACL': 'public-read'}
    )
    return [{
        'id': ident,
        'thumb_url': thumbnail_url,
        'filename': youtube_url
    }]


def presentation_files(upload_session_id: str, order_ids: list[str]) -> list[dict[str, str]]:
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )
    response = client.list_objects_v2(
        Bucket=config.DO_SPACE_BUCKET,
        Prefix=config.UPLOADED_PRODUCTS_DIR.format(upload_session_id=upload_session_id)
    )
    result = []
    for ident in order_ids:
        for content in response.get('Contents', []):
            if content['Key'].startswith(
                os.path.join(
                    config.UPLOADED_PRODUCTS_DIR.format(upload_session_id=upload_session_id),
                    'preview_'
                )
            ):
                do_target = content['Key'].split('_')[-1].split('.')[0]
                do_img_id = content['Key'].split('_')[-2]
                if do_img_id != ident:
                    continue
                if do_target == 'youtube':
                    result.append({
                        'type': 'youtube',
                        'url': get_s3_link(client, content['Key'])
                    })
                elif do_target == 'for-pb-preview':
                    result.append({
                        'type': 'img',
                        'url': get_s3_link(client, content['Key'])
                    })
    return result


def get_product_link(upload_session_id: str, new_name: str):
    filename = config.PRODUCT_S3_NAME_TEMPLATE.format(
        upload_session_id=upload_session_id
    )
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )
    new_filename = filename.replace('product.zip', f'{new_name}.zip')
    client.copy_object(
        Bucket=config.DO_SPACE_BUCKET,
        CopySource={'Bucket': config.DO_SPACE_BUCKET, 'Key': filename},
        Key=new_filename,
        ACL='public-read'
    )
    return get_s3_link(client, new_filename)


def get_product_size(upload_session_id: str):
    filename = config.PRODUCT_S3_NAME_TEMPLATE.format(
        upload_session_id=upload_session_id
    )
    local_session = s3_session.Session()
    client = local_session.client(
            's3',
            region_name=config.DO_SPACE_REGION,
            endpoint_url=config.DO_SPACE_ENDPOINT,
            aws_access_key_id=config.DO_SPACE_KEY,
            aws_secret_access_key=config.DO_SPACE_SECRET
        )
    response = client.head_object(
        Bucket=config.DO_SPACE_BUCKET,
        Key=filename
    )
    return response['ContentLength']
