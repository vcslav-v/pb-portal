APP_NAME = pb_portal
APP_AUTHOR = vaclav-v

CONTAINER_REGISTRY = dplace

FILE_LINT_SETTINGS = setup.cfg
FILE_GITIGNORE = .gitignore

RELAESE_ACTION_FILE = publish-on-relaese.yml

define DBPY
echo "from sqlalchemy import create_engine" >> $(APP_NAME)/db.py
echo "from sqlalchemy.orm import sessionmaker" >> $(APP_NAME)/db.py
echo "from os import environ" >> $(APP_NAME)/db.py
echo "" >> $(APP_NAME)/db.py
echo "if environ.get('DATABASE_URL'):" >> $(APP_NAME)/db.py
echo "    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL').replace(" >> $(APP_NAME)/db.py
echo "        'postgres', 'postgresql+psycopg2'" >> $(APP_NAME)/db.py
echo "    )" >> $(APP_NAME)/db.py
echo "else:" >> $(APP_NAME)/db.py
echo "    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:mysecretpassword@0.0.0.0/postgres'" >> $(APP_NAME)/db.py
echo "" >> $(APP_NAME)/db.py
echo "engine = create_engine(SQLALCHEMY_DATABASE_URI)" >> $(APP_NAME)/db.py
echo "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)" >> $(APP_NAME)/db.py

echo "from sqlalchemy import Column, Integer" >> $(APP_NAME)/models.py
echo "from sqlalchemy.ext.declarative import declarative_base" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "Base = declarative_base()" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "class Item(Base):" >> $(APP_NAME)/models.py
echo "    '''Items.'''" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "    __tablename__ = 'items'" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "    id = Column(Integer, primary_key=True)" >> $(APP_NAME)/models.py

endef

define MYPY_SETTINGS
echo "    # alembic" >> $(FILE_LINT_SETTINGS)
echo "    exclude = alembic/*" >> $(FILE_LINT_SETTINGS)
echo "[mypy]" >> $(FILE_LINT_SETTINGS)
echo "    plugins = sqlmypy" >> $(FILE_LINT_SETTINGS)

endef

define BOTPY
echo "import os" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "from loguru import logger" >> $(APP_NAME)/bot.py
echo "from telegram import Update" >> $(APP_NAME)/bot.py
echo "from telegram.ext import (Application, CommandHandler, ContextTypes," >> $(APP_NAME)/bot.py
echo "                          MessageHandler, filters)" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "BOT_TOKEN = os.environ.get('BOT_TOKEN', '')" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "@logger.catch" >> $(APP_NAME)/bot.py
echo "async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:" >> $(APP_NAME)/bot.py
echo "    '''Send a message when the command /start is issued.'''" >> $(APP_NAME)/bot.py
echo "    await update.message.reply_text('Hi!')" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "@logger.catch" >> $(APP_NAME)/bot.py
echo "async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:" >> $(APP_NAME)/bot.py
echo "    '''Echo the user message.'''" >> $(APP_NAME)/bot.py
echo "    await update.message.reply_text(update.message.text)" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "def main() -> None:" >> $(APP_NAME)/bot.py
echo "    '''Start the bot.'''" >> $(APP_NAME)/bot.py
echo "    application = Application.builder().token(BOT_TOKEN).build()" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "    application.add_handler(CommandHandler('start', start, filters.ChatType.PRIVATE))" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "    application.add_handler(MessageHandler(" >> $(APP_NAME)/bot.py
echo "        filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, echo" >> $(APP_NAME)/bot.py
echo "    ))" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "    application.run_polling()" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "" >> $(APP_NAME)/bot.py
echo "if __name__ == '__main__':" >> $(APP_NAME)/bot.py
echo "    main()" >> $(APP_NAME)/bot.py

endef

# private functions
_setup-lint:
	touch $(FILE_LINT_SETTINGS)
	@echo "[flake8]" >> $(FILE_LINT_SETTINGS)
	@echo "    max-line-length = 120" >> $(FILE_LINT_SETTINGS)

_setup-git-ignore:
	touch $(FILE_GITIGNORE)
	@echo ".venv" >> $(FILE_GITIGNORE)
	@echo "Makefile" >> $(FILE_GITIGNORE)
	@echo ".env" >> $(FILE_GITIGNORE)
	@echo ".vscode" >> $(FILE_GITIGNORE)
	@echo "*_cache" >> $(FILE_GITIGNORE)
	@echo "__pycache__" >> $(FILE_GITIGNORE)
	@echo ".python-version" >> $(FILE_GITIGNORE)
	@echo ".DS_Store" >> $(FILE_GITIGNORE)
	@echo "${FILE_LINT_SETTINGS}" >> $(FILE_GITIGNORE)


_setup-vscode:
	mkdir .vscode
	touch .vscode/settings.json
	@echo "{" >> .vscode/settings.json
	@echo "\"python.pythonPath\": \"`poetry env info --path`\"," >> .vscode/settings.json
	@echo "\"python.linting.pylintEnabled\": false," >> .vscode/settings.json
	@echo "\"python.linting.flake8Enabled\": true," >> .vscode/settings.json
	@echo "\"python.linting.mypyEnabled\": true," >> .vscode/settings.json
	@echo "\"python.linting.enabled\": true," >> .vscode/settings.json
	@echo "}" >> .vscode/settings.json
	jq -n '{"version": "0.2.0","configurations": []}' > .vscode/launch.json

_setup-github-realese-actions:
	@echo "name: Build and publish manually" > .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "on: [push]" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "jobs:" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "  build_and_push:" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "    runs-on: ubuntu-latest" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "    steps:" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "      - name: Checkout the repo" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "        uses: actions/checkout@v2" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "      - name: Build image" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "        run: docker build --build-arg GIT_TOKEN=\$$\{{ secrets.GIT_HUB_TOKEN }} -t vm ." >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "      - name: Install doctl" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "        uses: digitalocean/action-doctl@v2" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "        with:" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "          token: \$$\{{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "      - name: Log in to DO Container Registry" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "        run: doctl registry login --expiry-seconds 600" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "      - name: Tag image" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "        run: docker tag vm $(CONTAINER_REGISTRY)/$(APP_NAME):latest" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "      - name: Push image to DO Container Registry" >> .github/workflows/$(RELAESE_ACTION_FILE)
	@echo "        run: docker push $(CONTAINER_REGISTRY)/$(APP_NAME):latest" >> .github/workflows/$(RELAESE_ACTION_FILE)

_setup-config-file:
	@echo "import os" > $(APP_NAME)/config.py
	@echo "import sys" >> $(APP_NAME)/config.py
	@echo "from dotenv import load_dotenv" >> $(APP_NAME)/config.py
	@echo "from loguru import logger" >> $(APP_NAME)/config.py
	@echo "" >> $(APP_NAME)/config.py
	@echo "dotenv_path = os.path.join(os.path.dirname(__file__), '.env')" >> $(APP_NAME)/config.py
	@echo "if os.path.exists(dotenv_path):" >> $(APP_NAME)/config.py
	@echo "    logger.remove()" >> $(APP_NAME)/config.py
	@echo "    logger.add(sys.stderr, level='DEBUG')" >> $(APP_NAME)/config.py
	@echo "    IS_DEV = True" >> $(APP_NAME)/config.py
	@echo "    load_dotenv(dotenv_path)" >> $(APP_NAME)/config.py
	@echo "    logger.info('Loaded .env file')" >> $(APP_NAME)/config.py
	@echo "else:" >> $(APP_NAME)/config.py
	@echo "    logger.remove()" >> $(APP_NAME)/config.py
	@echo "    logger.add(sys.stderr, level='INFO')" >> $(APP_NAME)/config.py
	@echo "    IS_DEV = False" >> $(APP_NAME)/config.py
	@echo ""  >> $(APP_NAME)/config.py
	

_setup-fastapi-files:
	touch $(APP_NAME)/main.py
	mkdir $(APP_NAME)/api
	touch $(APP_NAME)/api/__init__.py
	touch $(APP_NAME)/api/routes.py

	mkdir $(APP_NAME)/api/local_routes
	touch $(APP_NAME)/api/local_routes/__init__.py
	touch $(APP_NAME)/api/local_routes/api.py


add-fastapi-vars-to-config:
	@echo "# FastAPI" >> $(APP_NAME)/config.py
	@echo "API_USERNAME = os.environ.get('API_USERNAME', 'api')"  >> $(APP_NAME)/config.py
	@echo "API_PASSWORD = os.environ.get('API_PASSWORD', 'pass')"  >> $(APP_NAME)/config.py
_setup-fastapi-routers:
	@echo "from fastapi import APIRouter" >> $(APP_NAME)/api/routes.py
	@echo "from $(APP_NAME).api.local_routes import api" >> $(APP_NAME)/api/routes.py
	@echo "" >> $(APP_NAME)/api/routes.py
	@echo "routes = APIRouter()" >> $(APP_NAME)/api/routes.py
	@echo "" >> $(APP_NAME)/api/routes.py
	@echo "routes.include_router(api.router, prefix='/api')" >> $(APP_NAME)/api/routes.py
_setup-fastapi-local-api:
	@echo "import os" >> $(APP_NAME)/api/local_routes/api.py
	@echo "import secrets" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "from fastapi import APIRouter, Depends, HTTPException, status" >> $(APP_NAME)/api/local_routes/api.py
	@echo "from fastapi.security import HTTPBasic, HTTPBasicCredentials" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "from $(APP_NAME) import config" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "router = APIRouter()" >> $(APP_NAME)/api/local_routes/api.py
	@echo "security = HTTPBasic()" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "username = config.API_USERNAME" >> $(APP_NAME)/api/local_routes/api.py
	@echo "password = config.API_PASSWORD" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):" >> $(APP_NAME)/api/local_routes/api.py
	@echo "    correct_username = secrets.compare_digest(credentials.username, username)" >> $(APP_NAME)/api/local_routes/api.py
	@echo "    correct_password = secrets.compare_digest(credentials.password, password)" >> $(APP_NAME)/api/local_routes/api.py
	@echo "    if not (correct_username and correct_password):" >> $(APP_NAME)/api/local_routes/api.py
	@echo "        raise HTTPException(" >> $(APP_NAME)/api/local_routes/api.py
	@echo "            status_code=status.HTTP_401_UNAUTHORIZED," >> $(APP_NAME)/api/local_routes/api.py
	@echo "            detail='Incorrect username or password'," >> $(APP_NAME)/api/local_routes/api.py
	@echo "            headers={'WWW-Authenticate': 'Basic'}," >> $(APP_NAME)/api/local_routes/api.py
	@echo "        )" >> $(APP_NAME)/api/local_routes/api.py
	@echo "    return credentials.username" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
	@echo "@router.get('/test')" >> $(APP_NAME)/api/local_routes/api.py
	@echo "async def test(_: str = Depends(get_current_username)):" >> $(APP_NAME)/api/local_routes/api.py
	@echo "    pass" >> $(APP_NAME)/api/local_routes/api.py
	@echo "" >> $(APP_NAME)/api/local_routes/api.py
_setup-fastapi-main:
	@echo "from fastapi import FastAPI" >> $(APP_NAME)/main.py
	@echo "from $(APP_NAME) import config" >> $(APP_NAME)/main.py
	@echo "from $(APP_NAME).api.routes import routes" >> $(APP_NAME)/main.py
	@echo "" >> $(APP_NAME)/main.py
	@echo "app = FastAPI(debug=config.IS_DEV)" >> $(APP_NAME)/main.py
	@echo "" >> $(APP_NAME)/main.py
	@echo "app.include_router(routes)" >> $(APP_NAME)/main.py
_setup-fastapi-vscode-launch:
	jq '.configurations += [{"name": "FastAPI", "type": "debugpy", "request": "launch", "module": "uvicorn", "args": ["'$(APP_NAME)'.main:app", "--reload"], "jinja": true}]' .vscode/launch.json > .vscode/temp_launch.json && mv .vscode/temp_launch.json .vscode/launch.json
_setup-fastapi-jinja-files:
	touch $(APP_NAME)/main.py
	touch $(APP_NAME)/dependencies.py
	mkdir $(APP_NAME)/routes
	touch $(APP_NAME)/routes/__init__.py
	touch $(APP_NAME)/routes/routes.py

	mkdir $(APP_NAME)/routes/local_routes
	touch $(APP_NAME)/routes/local_routes/__init__.py
	touch $(APP_NAME)/routes/local_routes/index.py

	mkdir $(APP_NAME)/templates
	touch $(APP_NAME)/templates/index.html
	touch $(APP_NAME)/templates/base.html

	mkdir $(APP_NAME)/static
	mkdir $(APP_NAME)/static/base
	mkdir $(APP_NAME)/static/base/css
	mkdir $(APP_NAME)/static/base/js
	mkdir $(APP_NAME)/static/base/img
	touch $(APP_NAME)/static/base/css/styles.css
add-fastapi-jinja-vars-to-config:
	@echo "# FastAPI" >> $(APP_NAME)/config.py
	@echo "API_USERNAME = os.environ.get('API_USERNAME', 'api')"  >> $(APP_NAME)/config.py
	@echo "API_PASSWORD = os.environ.get('API_PASSWORD', 'pass')"  >> $(APP_NAME)/config.py
	@echo "TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')"  >> $(APP_NAME)/config.py
	@echo "STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')"  >> $(APP_NAME)/config.py
_setup-fastapi-jinja-routers:
	@echo "from fastapi import APIRouter" >> $(APP_NAME)/routes/routes.py
	@echo "from $(APP_NAME).routes.local_routes import index" >> $(APP_NAME)/routes/routes.py
	@echo "" >> $(APP_NAME)/routes/routes.py
	@echo "routes = APIRouter()" >> $(APP_NAME)/routes/routes.py
	@echo "" >> $(APP_NAME)/routes/routes.py
	@echo "routes.include_router(index.router, prefix='')" >> $(APP_NAME)/routes/routes.py
_setup-fastapi-jinja-local-routes:
	@echo "from fastapi import APIRouter, Depends, Request" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "from fastapi.responses import HTMLResponse" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "from fastapi.templating import Jinja2Templates" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "from pb_portal import config, dependencies" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "router = APIRouter()" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "@config.logger.catch()" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "@router.get('/')" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "async def index(" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "    request: Request," >> $(APP_NAME)/routes/local_routes/index.py
	@echo "    templates: Jinja2Templates = Depends(dependencies.get_templates)," >> $(APP_NAME)/routes/local_routes/index.py
	@echo "    _: str = Depends(dependencies.get_current_username)" >> $(APP_NAME)/routes/local_routes/index.py
	@echo ") -> HTMLResponse:" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "    '''Index page.'''" >> $(APP_NAME)/routes/local_routes/index.py
	@echo "    return templates.TemplateResponse('index.html', {'request': request})" >> $(APP_NAME)/routes/local_routes/index.py
_setup-fastapi-jinja-main:
	@echo "from fastapi import FastAPI" >> $(APP_NAME)/main.py
	@echo "from fastapi.staticfiles import StaticFiles" >> $(APP_NAME)/main.py
	@echo "from fastapi.templating import Jinja2Templates" >> $(APP_NAME)/main.py
	@echo "from $(APP_NAME) import config" >> $(APP_NAME)/main.py
	@echo "from $(APP_NAME).routes.routes import routes" >> $(APP_NAME)/main.py
	@echo "" >> $(APP_NAME)/main.py
	@echo "app = FastAPI(debug=config.IS_DEV)" >> $(APP_NAME)/main.py
	@echo "app.mount('/static', StaticFiles(directory=config.STATIC_DIR), name='static')" >> $(APP_NAME)/main.py
	@echo "templates = Jinja2Templates(directory=config.TEMPLATES_DIR)" >> $(APP_NAME)/main.py
	@echo "" >> $(APP_NAME)/main.py
	@echo "app.include_router(routes)" >> $(APP_NAME)/main.py
_setup-fastapi-jinja-dependencies:
	@echo "import secrets" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "from fastapi import Depends, HTTPException, status" >> $(APP_NAME)/dependencies.py
	@echo "from fastapi.security import HTTPBasic, HTTPBasicCredentials" >> $(APP_NAME)/dependencies.py
	@echo "from fastapi.templating import Jinja2Templates" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "from pb_portal import config" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "security = HTTPBasic()" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "username = config.API_USERNAME" >> $(APP_NAME)/dependencies.py
	@echo "password = config.API_PASSWORD" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "def get_templates():" >> $(APP_NAME)/dependencies.py
	@echo "    return Jinja2Templates(directory=config.TEMPLATES_DIR)" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "" >> $(APP_NAME)/dependencies.py
	@echo "def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):" >> $(APP_NAME)/dependencies.py
	@echo "    correct_username = secrets.compare_digest(credentials.username, username)" >> $(APP_NAME)/dependencies.py
	@echo "    correct_password = secrets.compare_digest(credentials.password, password)" >> $(APP_NAME)/dependencies.py
	@echo "    if not (correct_username and correct_password):" >> $(APP_NAME)/dependencies.py
	@echo "        raise HTTPException(" >> $(APP_NAME)/dependencies.py
	@echo "            status_code=status.HTTP_401_UNAUTHORIZED," >> $(APP_NAME)/dependencies.py
	@echo "            detail='Incorrect username or password'," >> $(APP_NAME)/dependencies.py
	@echo "            headers={'WWW-Authenticate': 'Basic'}," >> $(APP_NAME)/dependencies.py
	@echo "        )" >> $(APP_NAME)/dependencies.py
	@echo "    return credentials.username" >> $(APP_NAME)/dependencies.py
_setup-start-site-template:
	@echo "<!DOCTYPE html>" > $(APP_NAME)/templates/base.html
	@echo "<html>" >> $(APP_NAME)/templates/base.html
	@echo "<head>" >> $(APP_NAME)/templates/base.html
	@echo "    <meta charset=\"UTF-8\">" >> $(APP_NAME)/templates/base.html
	@echo "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">" >> $(APP_NAME)/templates/base.html
	@echo "    <link rel=\"stylesheet\" href=\"{{ url_for('static', path='/base/css/styles.css') }}\">" >> $(APP_NAME)/templates/base.html
	@echo "    {% block head %}" >> $(APP_NAME)/templates/base.html
	@echo "    {% endblock %}" >> $(APP_NAME)/templates/base.html
	@echo "</head>" >> $(APP_NAME)/templates/base.html
	@echo "" >> $(APP_NAME)/templates/base.html
	@echo "<body>" >> $(APP_NAME)/templates/base.html
	@echo "    {% block header %}" >> $(APP_NAME)/templates/base.html
	@echo "    {% endblock %}" >> $(APP_NAME)/templates/base.html
	@echo "    {% block content %}" >> $(APP_NAME)/templates/base.html
	@echo "    {% endblock %}" >> $(APP_NAME)/templates/base.html
	@echo "    {% block footer %}" >> $(APP_NAME)/templates/base.html
	@echo "    {% endblock %}" >> $(APP_NAME)/templates/base.html
	@echo "</body>" >> $(APP_NAME)/templates/base.html
	@echo "" >> $(APP_NAME)/templates/base.html
	@echo "</html>" >> $(APP_NAME)/templates/base.html
	@echo "{% extends \"base.html\" %}" > $(APP_NAME)/templates/index.html
	@echo "{% block head %}" >> $(APP_NAME)/templates/index.html
	@echo "    <title>TEST</title>" >> $(APP_NAME)/templates/index.html
	@echo "{% endblock %}" >> $(APP_NAME)/templates/index.html
	@echo "{% block content %}" >> $(APP_NAME)/templates/index.html
	@echo "    <h1>Welcome to the TEST</h1>" >> $(APP_NAME)/templates/index.html
	@echo "{% endblock %}" >> $(APP_NAME)/templates/index.html
	@echo "body {" > $(APP_NAME)/static/base/css/styles.css
	@echo "    background-color: aquamarine;" >> $(APP_NAME)/static/base/css/styles.css
	@echo "}" >> $(APP_NAME)/static/base/css/styles.css

# public functions
init:
	poetry init -n --name $(APP_NAME) --author $(APP_AUTHOR)
	poetry add --dev flake8
	poetry add --dev mypy
	poetry add loguru
	poetry add python-dotenv
	make _setup-vscode
	make _setup-git-ignore
	make _setup-lint
	mkdir $(APP_NAME)
	touch $(APP_NAME)/__init__.py
	touch $(APP_NAME)/.env
	echo '"""Main module $(APP_NAME) project."""' > $(APP_NAME)/__init__.py
	make _setup-config-file
	mkdir .github
	mkdir .github/workflows
	touch .github/workflows/$(RELAESE_ACTION_FILE)
	make _setup-github-realese-actions
	poetry shell
fastapi:
	poetry add fastapi
	poetry add gunicorn
	poetry add uvicorn
	poetry add python-multipart
	poetry add pydantic

	make _setup-fastapi-files
	make add-fastapi-vars-to-config
	make _setup-fastapi-routers
	make _setup-fastapi-local-api
	make _setup-fastapi-main
	make _setup-fastapi-vscode-launch

fastapi_jinja:
	poetry add fastapi
	poetry add gunicorn
	poetry add uvicorn
	poetry add python-multipart
	poetry add pydantic
	poetry add jinja2
	poetry add aiofiles

	make _setup-fastapi-jinja-files
	make add-fastapi-jinja-vars-to-config
	make _setup-fastapi-jinja-routers
	make _setup-fastapi-jinja-local-routes
	make _setup-fastapi-jinja-main
	make _setup-fastapi-jinja-dependencies
	make _setup-start-site-template
	make _setup-fastapi-vscode-launch

db_revision:
	poetry run alembic revision --autogenerate

db_update:
	poetry run alembic upgrade head

test_db:
	docker run --name test-postgres -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=postgres -d -p 5432:5432 postgres

req:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# for revision
sqlalchemy:
	poetry add sqlalchemy
	poetry add psycopg2-binary
	poetry add alembic
	poetry run alembic init alembic
	$(MYPY_SETTINGS)
	touch $(APP_NAME)/models.py
	touch $(APP_NAME)/db.py
	$(DBPY)

tg_bot:
	poetry add git+https://github.com/python-telegram-bot/python-telegram-bot.git@master
	poetry add apscheduler
	touch $(APP_NAME)/bot.py
	$(BOTPY)

