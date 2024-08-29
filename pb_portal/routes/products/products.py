from fastapi import APIRouter, Depends, Request, Response, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pb_portal.auth.tools import current_active_user
from pb_portal.s3 import make_s3_url, rm_product, upload_pb_preview_image, rm_pb_preview, make_youtube_placeholder
from pb_portal import validate, imgs
from pb_portal.db.models import User
from pb_portal.auth.schemas import UserRoles
from fastapi.responses import RedirectResponse
import json
import os
from datetime import datetime, UTC
from typing import List


from pb_portal import config, dependencies

router = APIRouter()


@config.logger.catch()
@router.get('/')
async def products(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    if not user.signed_agreement_date:
        return RedirectResponse(request.url_for('agreement'))
    return templates.TemplateResponse('products/products.html', {
        'request': request,
        'user_role_id': user.role_id,
        'roles_schema': UserRoles,
        'user': user,
        'page_name': 'products',
    })


@config.logger.catch()
@router.get('/new')
async def new_product(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    if not user.signed_agreement_date:
        return RedirectResponse(request.url_for('agreement'))
    upload_session_id = f'{user.id}-{int(datetime.now(UTC).timestamp())}'
    return templates.TemplateResponse('products/new_product.html', {
        'request': request,
        'user_role_id': user.role_id,
        'roles_schema': UserRoles,
        'user': user,
        'page_name': 'products',
        'categories': json.loads(os.environ.get('PB_CATEGORIES', '{}')),
        'product_type': 'free',
        'sample_product_url': config.SAMPLE_PRODUCT_URL,
        'supported_formats': config.SUPPORTED_FORMATS,
        'upload_session_id': upload_session_id
    })


@router.post('/get_pricing_block')
async def get_pricing_block(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    form = await request.form()
    product_type = form.get('productType')
    return templates.TemplateResponse('products/_pricing.html', {
        'request': request,
        'product_type': product_type
    })


@router.post('/get_upload_product_url')
async def get_upload_product_url(
    request: Request,
    user: User = Depends(current_active_user)
):
    form = await request.form()
    json_result = make_s3_url(
        upload_session_id=form.get('upload_session_id', 'error'),
        content_type='application/zip',
    )
    return Response(content=json_result, media_type='application/json')


@router.post('/rm_upload_product_url')
async def rm_upload_product_url(
    request: Request,
    user: User = Depends(current_active_user)
):
    form = await request.form()
    rm_product(
        upload_session_id=form.get('upload_session_id', 'error')
    )
    return Response(content='{"status": "ok"}', media_type='application/json')


@router.post('/validate_description')
async def validate_description(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    description = form.get('description', '')
    length, forbidden_tags = validate.description(description)
    if forbidden_tags:
        text_line = 'Only bold, italic, and lists are allowed'
    else:
        text_line = ''
    return templates.TemplateResponse('products/_text_counter.html', {
        'request': request,
        'len_items': length,
        'max_len': config.MAX_DESCRIPTION_LENGTH,
        'target_id': 'descriptionCounter',
        'text_line': text_line,
    })


@router.post('/validate_excerpt')
async def validate_excerpt(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user),
):
    form = await request.form()
    excerpt = form.get('excerpt', '')
    length, text_line = validate.exerpt(excerpt)
    return templates.TemplateResponse('products/_text_counter.html', {
        'request': request,
        'len_items': length,
        'max_len': config.MAX_EXERPT_LENGTH,
        'target_id': 'excerptCounter',
        'text_line': text_line,
    })


@router.post('/validate_tags')
async def validate_tags(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    tags_str = form.get('tags', '')
    tags, text_line = validate.tags(tags_str)
    return templates.TemplateResponse('products/_tag_list.html', {
        'request': request,
        'tags': tags,
        'tag_len': len(tags),
        'text_line': text_line,
    })


@router.post('/count_tags')
async def count_tags(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    tag_len = form.get('tag_len', '0')
    tag_len = int(tag_len) if tag_len.isdigit() else 0
    text_line = form.get('text_line', '')
    return templates.TemplateResponse('products/_text_counter.html', {
        'request': request,
        'len_items': tag_len,
        'max_len': config.MAX_TAGS_LENGTH,
        'target_id': 'tagsCounter',
        'text_line': text_line,
    })


@router.post('/imgs_upload', response_class=HTMLResponse)
async def imgs_upload(
    request: Request,
    user: User = Depends(current_active_user),
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    imgFiles: List[UploadFile] = File(...)
):
    form = await request.form()
    upload_session_id = form.get('upload_session_id', 'error')
    validated_imgs = []
    for imgFile in imgFiles:
        if imgFile.content_type != 'image/jpeg':
            validated_imgs.append((None, None, 'Only JPEG images are allowed', imgFile.filename))
            continue
        if imgFile.size > config.MAX_IMAGE_SIZE:
            validated_imgs.append((None, None, 'Image size is too big', imgFile.filename))
            continue
        validated_imgs.append(imgs.prepare_pb_preview_image(imgFile.file.read(), imgFile.filename))
    return templates.TemplateResponse('products/_sort_imgs.html', {
        'request': request,
        'imgs': upload_pb_preview_image(validated_imgs, upload_session_id),
    })


@router.delete('/delete_img')
async def delete_img(
    request: Request,
    user: User = Depends(current_active_user),
):
    form = await request.form()
    img_id = form.get('img_id')
    upload_session_id = form.get('upload_session_id', 'error')
    if img_id:
        rm_pb_preview(img_id, upload_session_id)
    return Response(content='<!-- Removed -->', media_type='application/json')


@router.post('/add_youtube_preview')
async def add_youtube_preview(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user),
):
    form = await request.form()
    youtube_url = form.get('youtubeLink', '')
    upload_session_id = form.get('upload_session_id', 'error')
    youtube_thumbnail = validate.youtube_thumbnail(youtube_url)
    return templates.TemplateResponse('products/_sort_imgs.html', {
        'request': request,
        'imgs': make_youtube_placeholder(youtube_url, upload_session_id, youtube_thumbnail),
    })
