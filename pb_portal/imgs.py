from PIL import Image
import io
from pb_portal import config


def prepare_pb_preview_image(image: bytes, filename: str) -> tuple[io.BytesIO | None, io.BytesIO | None, str, str]:
    img = Image.open(io.BytesIO(image))
    if img.width < config.MIN_PB_IMAGE_WIDTH or img.height < config.MIN_PB_IMAGE_HEIGHT:
        return None, None, 'Image has to be at least 2250x1500 pixels', filename

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
