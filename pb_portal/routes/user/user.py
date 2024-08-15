from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pb_portal import config, dependencies
from pb_portal.auth.tools import optional_active_user, current_superuser
from pb_portal.db.models import User
from pb_portal.db.tools import get_users, rm_user, edit_user as db_edit_user, get_user, create_user as db_create_user
from pb_portal.auth.schemas import UserRoles
from pb_portal.auth.manager import get_user_manager


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
    return templates.TemplateResponse('auth/auth.html', {'request': request})


@config.logger.catch()
@router.get('/manage')
async def manage(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    user: User = Depends(current_superuser)
) -> HTMLResponse:
    '''User management page'''
    return templates.TemplateResponse('users_manage/users_manage.html', {
        'request': request,
        'user_role_id': user.role_id,
        'roles_schema': UserRoles,
        'users': await get_users(),
        'page_name': 'manage_users'
    })


@config.logger.catch()
@router.post('/edit/{user_id}')
async def edit_user(
    request: Request,
    user_id: int,
    email: str = Form(...),
    password: str = Form(...),
    role: int = Form(...),
    action: str = Form(...),
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    _: User = Depends(current_superuser)
) -> HTMLResponse:
    '''Edit user role'''
    if action == 'edit':
        if password == 'empty':
            pswd = None
        else:
            async for mng in get_user_manager():
                pswd = mng.password_helper.hash(password)
        await db_edit_user(user_id, email, role, pswd)
        edit_user = await get_user(user_id)
        return templates.TemplateResponse('users_manage/user_row.html', {
            'request': request,
            'user': edit_user,
            'roles_schema': UserRoles,
        })
    elif action == 'delete':
        await rm_user(user_id)
        return ''
    return RedirectResponse(request.url_for('manage'))


@config.logger.catch()
@router.get('/new_user')
def new_user_row(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    _: User = Depends(current_superuser)
) -> HTMLResponse:
    '''New user row'''
    return templates.TemplateResponse('users_manage/new_user_row.html', {
        'request': request,
        'roles_schema': UserRoles,
    }
    )


@config.logger.catch()
@router.post('/create')
async def create(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    role: int = Form(...),
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    _: User = Depends(current_superuser)
) -> HTMLResponse:
    '''Create new user'''
    async for mng in get_user_manager():
        pswd = mng.password_helper.hash(password)
    user = await db_create_user(email, pswd, role)
    return templates.TemplateResponse('users_manage/user_row.html', {
        'request': request,
        'user': user,
        'roles_schema': UserRoles,
    })
