from flask import Blueprint, render_template, request, send_file
from loguru import logger
from pb_portal import connectors

app_route = Blueprint('route', __name__, url_prefix='/graphics-tools')


@logger.catch
@app_route.route('/', methods=['GET', 'POST'])
def graphics_tools():
    return render_template(
        'graphics_tools.html',
    )


@logger.catch
@app_route.route('/tinify', methods=['POST'])
def tinify():
    try:
        zip_file = connectors.graphic.get_tiny_zip(
            request.files.getlist('forTiny'),
            request.form.get('resize_width')
        )
    except Exception as e:
        logger.error(e.args)
        return
    return send_file(zip_file, mimetype='application/x-zip-compressed')


@logger.catch
@app_route.route('/longy', methods=['POST'])
def longy():
    try:
        long_jpg = connectors.graphic.get_long_jpg(
            request.files.getlist('forLong'),
        )
    except Exception as e:
        logger.error(e.args)
        return
    return send_file(long_jpg, mimetype='image/jpeg')
