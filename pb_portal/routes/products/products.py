from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pb_portal.auth.tools import current_active_user
from pb_portal.s3 import make_s3_url
from pb_portal.db.models import User
from pb_portal.auth.schemas import UserRoles
from fastapi.responses import RedirectResponse
import json
import os
from datetime import datetime, UTC


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
    return make_s3_url(
        filename=form.get('upload_session_id', 'error')+'.zip',
        content_type='application/zip',
    )
