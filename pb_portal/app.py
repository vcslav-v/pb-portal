from flask import Flask, redirect, url_for
from flask_httpauth import HTTPBasicAuth

from pb_portal import routes

app = Flask(__name__)
auth = HTTPBasicAuth()
app.register_blueprint(routes.graphic_tools.app_route, name='graphics_tools')
app.register_blueprint(routes.drbl_like.app_route, name='drbl_like')
app.register_blueprint(routes.money.app_route, name='money')
app.register_blueprint(routes.tag_board.app_route, name='tag_board')


@app.route('/')
def index():
    return redirect(url_for('tag_board.tag_board'))
