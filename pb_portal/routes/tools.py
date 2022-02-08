from flask import Blueprint, render_template, request, send_file
from loguru import logger
from pb_portal import connectors

app_route = Blueprint('route', __name__, url_prefix='/tools')


@logger.catch
@app_route.route('/graphics', methods=['GET'])
def graphics():
    return render_template(
        'graphics_tools.html',
    )


@logger.catch
@app_route.route('/utm', methods=['GET'])
def utm():
    return render_template(
        'utm_tools.html',
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


@logger.catch
@app_route.route('/gify', methods=['POST'])
def gify():
    try:
        result_gif = connectors.graphic.get_gif(
            request.form.get('seq_prefix') or '',
            int(request.form.get('frames_per_sec')) if request.form.get('frames_per_sec') else None,
            request.files.getlist('forGif'),
        )
    except Exception as e:
        logger.error(e.args)
        return
    return send_file(result_gif, mimetype='image/gif')


@logger.catch
@app_route.route('/get_utm', methods=['POST'])
def get_utm():
    return connectors.link_dealer.get_utm(**request.form.to_dict()).json()
