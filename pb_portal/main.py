from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pb_portal import config
from pb_portal.routes.routes import routes
from contextlib import asynccontextmanager
from pb_portal.db.tools import prepare_user_roles
from pb_portal import exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.logger.info('Starting app')
    await prepare_user_roles()
    yield
    config.logger.info('Stopping app')

app = FastAPI(debug=config.IS_DEV, lifespan=lifespan)
app.mount('/static', StaticFiles(directory=config.STATIC_DIR), name='static')
templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

app.include_router(routes)
app.add_exception_handler(HTTPException, exception_handlers.http_exception_handler)
