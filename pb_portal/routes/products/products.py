from fastapi import APIRouter, Depends, Request, Response, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pb_portal.auth.tools import current_active_user
from pb_portal.s3 import make_s3_url, rm_product, upload_pb_preview_image, rm_pb_preview, make_youtube_placeholder
from pb_portal import validate, imgs
from pb_portal.db.models import User
from pb_portal.auth.schemas import UserRoles
from pb_portal.schemas.new_product import UploadForm, Preview, UploaderResponse
from pb_portal.pb import upload_product, add_product_file
from fastapi.responses import RedirectResponse
import json
import os
from datetime import datetime, UTC
from typing import List
import base64
from threading import Thread


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


def get_upload_session(request: Request, user: User) -> UploadForm:
    upload_session = request.cookies.get('upload_session')
    if upload_session:
        try:
            upload_session_decoded = base64.b64decode(upload_session).decode('utf-8')
            upload_session = json.loads(upload_session_decoded)
        except Exception as e:
            upload_session = {'session_id': f'{user.id}-{int(datetime.now(UTC).timestamp())}'}
    else:
        upload_session = {'session_id': f'{user.id}-{int(datetime.now(UTC).timestamp())}'}
    upload_session = UploadForm(**upload_session)
    return upload_session


def set_upload_session(response: Response, upload_session: UploadForm) -> None:
    upload_session_data = upload_session.model_dump_json().encode('utf-8')
    upload_session_encoded = base64.b64encode(upload_session_data).decode('utf-8')
    response.set_cookie(
        'upload_session',
        upload_session_encoded,
        max_age=3600,
    )


def add_preview_to_upload_session(prepared_imgs: list[dict[str, str]], upload_session: UploadForm) -> None:
    for img in prepared_imgs:
        if img.get('error'):
            continue
        upload_session.previews.append(Preview.model_validate(img))


def rm_preview_from_upload_session(img_id: str, upload_session: UploadForm) -> None:
    for preview in upload_session.previews:
        if preview.id == img_id:
            upload_session.previews.remove(preview)
            break


@config.logger.catch()
@router.get('/new')
async def new_product(
    request: Request,
    response: Response,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    if not user.signed_agreement_date:
        return RedirectResponse(request.url_for('agreement'))
    upload_session = get_upload_session(request, user)
    set_upload_session(response, upload_session)
    return templates.TemplateResponse(
        'products/new_product.html',
        {
            'request': request,
            'user_role_id': user.role_id,
            'roles_schema': UserRoles,
            'user': user,
            'page_name': 'products',
            'categories': json.loads(os.environ.get('PB_CATEGORIES', '{}')),
            'creators': json.loads(os.environ.get('PB_CREATORS', '{}')),
            'product_type': 'free',
            'sample_product_url': config.SAMPLE_PRODUCT_URL,
            'supported_formats': config.SUPPORTED_FORMATS,
            'upload_session': upload_session,
            'previews': upload_session.previews,
        },
        headers=response.headers
    )


@router.post('/save_product_title')
async def save_product_title(
    request: Request,
    response: Response,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    upload_session = get_upload_session(request, user)
    upload_session.title = form.get('title', '')
    set_upload_session(response, upload_session)
    return templates.TemplateResponse(
        'products/_title_input.html',
        {
            'request': request,
            'title': upload_session.title,
        },
        headers=response.headers
    )


@router.post('/save_changes')
async def save_changes(
    request: Request,
    response: Response,
    user: User = Depends(current_active_user)
):
    form = await request.form()
    upload_session = get_upload_session(request, user)
    upload_session.category_id = form.get('category', '')
    upload_session.creator_id = form.get('creator_id', '')
    upload_session.commercial_price = form.get('commercialPrice', '')
    upload_session.extended_price = form.get('extendedPrice', '')
    upload_session.product_name = form.get('productName', '')
    upload_session.formats = form.getlist('formats[]')
    upload_session.desc = form.get('hiddenDescription', '')
    set_upload_session(response, upload_session)
    return Response(content='<!-- Saved -->', media_type='application/json', headers=response.headers)


@router.post('/get_pricing_block')
async def get_pricing_block(
    request: Request,
    response: Response,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    form = await request.form()
    upload_session = get_upload_session(request, user)
    upload_session.product_type = form.get('productType', '')
    set_upload_session(response, upload_session)

    return templates.TemplateResponse(
        'products/_pricing.html', 
        {
            'request': request,
            'upload_session': upload_session
        },
        headers=response.headers
    )


@router.post('/get_upload_product_url')
async def get_upload_product_url(
    request: Request,
    user: User = Depends(current_active_user)
):
    upload_sesion = get_upload_session(request, user)
    json_result = make_s3_url(
        upload_session_id=upload_sesion.session_id,
        content_type='application/zip',
    )
    return Response(content=json_result, media_type='application/json')


@router.post('/rm_upload_product_url')
async def rm_upload_product_url(
    request: Request,
    user: User = Depends(current_active_user)
):
    upload_sesion = get_upload_session(request, user)
    rm_product(
        upload_session_id=upload_sesion.session_id,
    )
    return Response(content='{"status": "ok"}', media_type='application/json')


@router.post('/validate_description')
async def validate_description(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    upload_session = get_upload_session(request, user)
    description = form.get('description', '')
    if not description:
        length = 0
        text_line = 'Type any description' if upload_session.errors.desc else ''
    else:
        length, forbidden_tags = validate.description(description)
        text_line = 'Only bold, italic, and lists are allowed' if forbidden_tags else ''

    return templates.TemplateResponse(
        'products/_text_counter.html',
        {
            'request': request,
            'len_items': length,
            'max_len': config.MAX_DESCRIPTION_LENGTH,
            'target_id': 'descriptionCounter',
            'text_line': text_line,
        },
    )


@router.post('/validate_excerpt')
async def validate_excerpt(
    request: Request,
    response: Response,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user),
):
    form = await request.form()
    upload_session = get_upload_session(request, user)
    upload_session.exerpt = form.get('excerpt', '')
    set_upload_session(response, upload_session)
    length, text_line = validate.exerpt(upload_session.exerpt)
    return templates.TemplateResponse(
        'products/_text_counter.html',
        {
            'request': request,
            'len_items': length,
            'max_len': config.MAX_EXERPT_LENGTH,
            'target_id': 'excerptCounter',
            'text_line': text_line,
        },
        headers=response.headers
    )


@router.post('/validate_tags')
async def validate_tags(
    request: Request,
    response: Response,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    upload_session = get_upload_session(request, user)
    upload_session.tags = form.get('tags', '')
    set_upload_session(response, upload_session)
    tags, text_line = validate.tags(upload_session.tags)
    return templates.TemplateResponse(
        'products/_tag_list.html',
        {
            'request': request,
            'tags': tags,
            'tag_len': len(tags),
            'text_line': text_line,
        },
        headers=response.headers
    )


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
    response: Response,
    user: User = Depends(current_active_user),
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    imgFiles: List[UploadFile] = File(...)
):
    upload_session = get_upload_session(request, user)
    validated_imgs = []
    for imgFile in imgFiles:
        if imgFile.content_type != 'image/jpeg':
            validated_imgs.append((None, None, 'Only JPEG images are allowed', imgFile.filename))
            continue
        if imgFile.size > config.MAX_IMAGE_SIZE:
            validated_imgs.append((None, None, 'Image size is too big', imgFile.filename))
            continue
        validated_imgs.append(imgs.prepare_pb_preview_image(imgFile.file.read(), imgFile.filename))
    prepared_imgs = upload_pb_preview_image(validated_imgs, upload_session.session_id)
    add_preview_to_upload_session(prepared_imgs, upload_session)
    set_upload_session(response, upload_session)
    return templates.TemplateResponse(
        'products/_sort_imgs.html',
        {
            'request': request,
            'previews': prepared_imgs,
        },
        headers=response.headers
    )


@router.delete('/delete_img')
async def delete_img(
    request: Request,
    response: Response,
    user: User = Depends(current_active_user),
):
    form = await request.form()
    img_id = form.get('img_id')
    upload_session = get_upload_session(request, user)
    rm_preview_from_upload_session(img_id, upload_session)
    set_upload_session(response, upload_session)
    if img_id:
        rm_pb_preview(img_id, upload_session.session_id)
    return Response(content='<!-- Removed -->', media_type='application/json', headers=response.headers)


@router.post('/save_sort_img_changes')
async def save_sort_img_changes(
    request: Request,
    response: Response,
    user: User = Depends(current_active_user),
):
    form = await request.form()
    preview_ids = form.getlist('preview_ids[]')
    preview_ids = [int(preview_id) for preview_id in preview_ids]
    upload_session = get_upload_session(request, user)
    upload_session.previews = [preview for preview in upload_session.previews if preview.id in preview_ids]
    upload_session.previews = sorted(upload_session.previews, key=lambda x: preview_ids.index(x.id))
    set_upload_session(response, upload_session)
    return Response(content='<!-- Saved -->', media_type='application/json', headers=response.headers)


@router.post('/add_youtube_preview')
async def add_youtube_preview(
    request: Request,
    response: Response,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user),
):
    form = await request.form()
    youtube_url = form.get('youtubeLink', '')
    upload_session = get_upload_session(request, user)
    youtube_thumbnail = validate.youtube_thumbnail(youtube_url)
    prepared = make_youtube_placeholder(youtube_url, upload_session.session_id, youtube_thumbnail)
    add_preview_to_upload_session(prepared, upload_session)
    set_upload_session(response, upload_session)
    return templates.TemplateResponse(
        'products/_sort_imgs.html',
        {
            'request': request,
            'previews': prepared,
        },
        headers=response.headers
    )


@router.post('/submit_btn_text')
async def submit_btn_text(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user),
):
    form = await request.form()
    schedule_date = form.get('schedule_date', '')
    return templates.TemplateResponse(
        'products/_submit_btn_text.html',
        {
            'request': request,
            'schedule_date': schedule_date,
        },
    )


@router.post('/schedule_info')
async def schedule_info(
    request: Request,
    response: Response,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user),
):
    form = await request.form()
    schedule_date = form.get('schedule_date', '')
    upload_session = get_upload_session(request, user)
    formated_date = ''
    if schedule_date:
        formated_date = datetime.strptime(schedule_date, '%Y-%m-%d %H:%M').strftime('%d %b %Y, %H:%M')
        upload_session.schedule_date = schedule_date
    else:
        upload_session.schedule_date = ''
    set_upload_session(response, upload_session)
    return templates.TemplateResponse(
        'products/_schedule_info.html',
        {
            'request': request,
            'response': response,
            'formated_date': formated_date,
        },
        headers=response.headers
    )


@router.post('/submit_new_product')
async def submit_new_product(
    request: Request,
    response: Response,
    user: User = Depends(current_active_user),
):
    upload_session = get_upload_session(request, user)
    form = await request.form()
    is_valid = validate.upload_form(upload_session, form)

    if is_valid:
        upload_product_thread = Thread(
            target=upload_product,
            args=(form, user)
        )
        upload_product_thread.start()
        # response.delete_cookie('upload_session') 
        return RedirectResponse(
            request.url_for('products'),
            status_code=303,
            headers=response.headers
        )
    else:
        set_upload_session(response, upload_session)
        return RedirectResponse(
            request.url_for('new_product'),
            status_code=303,
            headers=response.headers
        )


@router.post('/push_uploader_links/{product_id}')
def push_uploader_links(product_id: str, uploader_resp: UploaderResponse):
    add_product_file(uploader_resp, product_id)
