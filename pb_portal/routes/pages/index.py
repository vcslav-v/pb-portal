from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from pb_portal import config, dependencies

router = APIRouter()


@config.logger.catch()
@router.get('/')
async def index(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.get_templates),
    _: str = Depends(dependencies.get_current_username)
) -> HTMLResponse:
    '''Index page.'''
    return templates.TemplateResponse('index.html', {'request': request})
