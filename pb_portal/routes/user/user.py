from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pb_portal import config, dependencies
from pb_portal.auth.tools import optional_active_user, current_superuser
from pb_portal.db.models import User
from pb_portal.auth.schemas import UserRoles

router = APIRouter()


@config.logger.catch()
@router.get('/login')
async def login(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User | None = Depends(optional_active_user)
) -> HTMLResponse:
    '''Authorization page'''
    if user:
        return RedirectResponse(request.url_for('index'))
    return templates.TemplateResponse('auth.html', {'request': request})


@config.logger.catch()
@router.get('/manage')
async def manage(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_superuser)
) -> HTMLResponse:
    '''User management page'''
    return templates.TemplateResponse('users_manage.html', {
        'request': request,
        'user_role_id': user.role_id,
        'roles_schema': UserRoles
    })
