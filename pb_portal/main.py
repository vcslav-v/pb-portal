from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pb_portal import config
from pb_portal.routes.routes import routes

app = FastAPI(debug=config.IS_DEV)
app.mount('/static', StaticFiles(directory=config.STATIC_DIR), name='static')
templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

app.include_router(routes)
