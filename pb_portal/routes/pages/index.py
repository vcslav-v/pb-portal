from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pb_portal.auth.tools import current_active_user
from pb_portal.db.models import User
from pb_portal.auth.schemas import UserRoles
from fastapi.responses import RedirectResponse

from pb_portal import config, dependencies

router = APIRouter()


@config.logger.catch()
@router.get('/')
async def index(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_active_user)
) -> HTMLResponse:
    '''Index page.'''
    if not user:
        return RedirectResponse(request.url_for('login'))
    return templates.TemplateResponse('index.html', {
        'request': request,
        'user_role_id': user.role_id,
        'roles_schema': UserRoles
    })
