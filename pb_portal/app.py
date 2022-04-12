from flask import Flask, redirect, url_for
from flask_httpauth import HTTPBasicAuth

from pb_portal import routes

app = Flask(__name__)
auth = HTTPBasicAuth()
app.register_blueprint(routes.tools.app_route, name='tools')
app.register_blueprint(routes.drbl_like.app_route, name='drbl_like')
app.register_blueprint(routes.money.app_route, name='money')
app.register_blueprint(routes.reports.app_route, name='reports')
app.register_blueprint(routes.tag_board.app_route, name='tag_board')
app.register_blueprint(routes.products.app_route, name='products')


@app.route('/')
def index():
    return redirect(url_for('tag_board.tag_board'))
