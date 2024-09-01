from PIL import Image
import io
from pb_portal import config
from pb_admin import schemas as pb_schemas
import requests


def prepare_pb_preview_image(image: bytes, filename: str) -> tuple[io.BytesIO | None, io.BytesIO | None, str, str]:
    img = Image.open(io.BytesIO(image))
    if img.width < config.MIN_PB_IMAGE_WIDTH or img.height < config.MIN_PB_IMAGE_HEIGHT:
        return None, None, 'Image has to be at least 2080x1386 pixels', filename

    aspect_ratio = img.width / img.height
    if round(aspect_ratio, 2) != round(config.PB_IMAGE_ASPECT_RATIO, 2):
        return None, None, 'Aspect ratio has to be 3/2', filename

    img.thumbnail((config.MAX_IMAGE_WIDTH, config.MAX_IMAGE_HEIGHT))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    portal_bytes = io.BytesIO()
    img.thumbnail((config.PORTAL_PREVIEW_IMAGE_WIDTH, config.PORTAL_PREVIEW_IMAGE_HEIGHT))
    img.save(portal_bytes, format='JPEG')
    portal_bytes.seek(0)
    return img_bytes, portal_bytes, '', filename


def get_pb_graphics(presentation_urls: list[dict[str, str]], slug: str, title: str) -> tuple[
    pb_schemas.Image,
    pb_schemas.Image,
    list[pb_schemas.Image],
    list[list[pb_schemas.ProductLayoutImg | pb_schemas.ProductLayoutVideo]]
]:
    thumbnail = None
    push_image = None
    images = []
    presentation = []
    img_n = 0
    for item in presentation_urls:
        if item['type'] == 'img':
            resp = requests.get(item['url'])
            if resp.status_code != 200:
                continue
            img = Image.open(io.BytesIO(resp.content))
            img.thumbnail((config.MIN_PB_IMAGE_WIDTH, config.MIN_PB_IMAGE_HEIGHT))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            images.append(pb_schemas.Image(
                file_name=f'{slug}_{img_n}.jpg',
                mime_type='image/jpeg',
                data=img_bytes.read(),
                alt=title,
            ))
            presentation.append([pb_schemas.ProductLayoutImg(img_n=img_n)])
            img_n += 1
            if not thumbnail:
                img.thumbnail((config.THUMBNAIL_WIDTH, config.THUMBNAIL_HEIGHT))
                thumbnail_bytes = io.BytesIO()
                img.save(thumbnail_bytes, format='JPEG')
                thumbnail_bytes.seek(0)
                thumbnail = pb_schemas.Image(
                    file_name=f'{slug}_thumbnail.jpg',
                    mime_type='image/jpeg',
                    data=thumbnail_bytes.read(),
                    alt=title,
                )
            if not push_image:
                img.thumbnail((config.THUMBNAIL_WIDTH, config.PUSH_IMAGE_HEIGHT))
                left = (img.width - config.PUSH_IMAGE_WIDTH) / 2
                top = (img.height - config.PUSH_IMAGE_HEIGHT) / 2
                right = (img.width + config.PUSH_IMAGE_WIDTH) / 2
                bottom = (img.height + config.PUSH_IMAGE_HEIGHT) / 2
                img = img.crop((left, top, right, bottom))
                push_image_bytes = io.BytesIO()
                img.save(push_image_bytes, format='JPEG')
                push_image_bytes.seek(0)
                push_image = pb_schemas.Image(
                    file_name=f'{slug}_push.jpg',
                    mime_type='image/jpeg',
                    data=push_image_bytes.read(),
                    alt=title,
                )
        elif item['type'] == 'youtube':
            resp = requests.get(item['url'])
            if resp.status_code != 200:
                continue
            presentation.append([pb_schemas.ProductLayoutVideo(
                title=title,
                link=resp.text,
            )])
    return thumbnail, push_image, images, presentation
