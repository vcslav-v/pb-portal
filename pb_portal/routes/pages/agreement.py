from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pb_portal.auth.tools import current_active_user
from pb_portal.db.models import User
from pb_portal.db.tools import sign_agreement as db_sign_agreement
from pb_portal.auth.schemas import UserRoles
from fastapi.responses import RedirectResponse

from pb_portal import config, dependencies

router = APIRouter()


@config.logger.catch()
@router.get('/')
async def agreement(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    if not user:
        return RedirectResponse(request.url_for('login'))
    return templates.TemplateResponse('agreement/agreement.html', {
        'request': request,
        'user_role_id': user.role_id,
        'roles_schema': UserRoles,
        'user': user,
        'page_name': 'agreement'
    })


@config.logger.catch()
@router.post('/sign_agreement')
async def sign_agreement(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    is_agree: bool = Form(...),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    '''Edit user role'''
    if is_agree:
        signed_user = await db_sign_agreement(user.id)
    signed_user = signed_user if signed_user else user
    return templates.TemplateResponse('agreement/agreement_footer.html', {
        'request': request,
        'user': signed_user,
    })
