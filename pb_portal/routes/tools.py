import os
import shutil
import zipfile

from flask import (Blueprint, flash, redirect, render_template, request,
                   send_file, url_for)
from loguru import logger
from pb_portal import connectors
from pydantic import ValidationError
from datetime import datetime

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
@app_route.route('/neuro', methods=['GET', 'POST'])
def neuro():
    gpt_results = ['']
    last_prompt = ''
    last_tokens = ''
    last_quantity = ''
    if request.method == 'POST':
        params = connectors.neuro.schemas.TextGPT(
            prompt=request.form.get('prompt')
        )
        last_prompt = request.form.get('prompt')
        if request.form.get('tokens') and request.form.get('tokens').isdigit():
            params.tokens = int(request.form.get('tokens'))
            last_tokens = request.form.get('tokens')
        if request.form.get('quantity') and request.form.get('quantity').isdigit():
            params.quantity = int(request.form.get('quantity'))
            last_quantity = request.form.get('quantity')
        gpt_results = connectors.neuro.get_gpt_text(params)
    return render_template(
        'neuro.html',
        gpt_results=gpt_results,
        last_prompt=last_prompt,
        last_tokens=last_tokens,
        last_quantity=last_quantity,
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
            request.form.get('width'),
            request.form.get('height'),
            request.form.get('n_cols'),
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


@logger.catch
@app_route.route('/all-videos', methods=['GET'])
def all_videos():
    page = connectors.video.get_page()
    return render_template(
        'videos_list.html',
        page=page,
    )


@logger.catch
@app_route.route('/rm-video', methods=['POST'])
def rm_video():
    connectors.video.rm_video(request.form.get('uid'))
    return "200"


@logger.catch
@app_route.route('/dwn-video', methods=['POST'])
def dwn_video():
    return connectors.video.get_link(request.form.get('uid'))


@logger.catch
@app_route.route('/video-template-1', methods=['GET', 'POST'])
def video_template_1():
    if request.method == 'GET':
        return render_template(
            'video_template_1.html',
        )
    elif request.method == 'POST':
        try:
            t1_data = connectors.video.schemas.Template1(
                background_color=request.form.get('t1_bg_color'),
                text_colour=request.form.get('t1_text_color'),
                title=request.form.get('t1_title'),
                sub_title=request.form.get('t1_subtitle'),
                final_text=request.form.get('t1_final_text'),
                time_cover=request.form.get('t1_cover_time'),
                time_shot=request.form.get('t1_shot_time'),
                time_final=request.form.get('t1_final_time'),
                music=request.form.get('t1_music'),
            )
        except ValidationError:
            flash('Wrong data', category='error')
            return redirect(url_for('tools.video_template_1'))
        name = ' '.join(t1_data.title)
        temp_dir_name = f'video_template_files-{datetime.utcnow().strftime("%Y%m%d%H%M%S%f")}'
        os.makedirs(temp_dir_name)
        zip_name = 'out.zip'
        try:
            video_template_file_prepare(temp_dir_name, t1_data, request.files.lists(), zip_name)
        except Exception:
            shutil.rmtree(temp_dir_name)
            flash('Wrong imgs', category='error')
            return redirect(url_for('tools.video_template_1'))
        try:
            connectors.video.make_video_t1(os.path.join(temp_dir_name, zip_name), name)
        except Exception:
            shutil.rmtree(temp_dir_name)
            flash('System error', category='error')
            return redirect(url_for('tools.video_template_1'))

        shutil.rmtree(temp_dir_name)
        flash('New task is added')
        return redirect(url_for('tools.all_videos'))


def video_template_file_prepare(temp_dir_name, t1_data, files, zip_name):
    with open(os.path.join(temp_dir_name, 'settings.json'), 'w') as settings_file:
        settings_file.write(t1_data.json())

    for file_req in files:
        field_name, field_data = file_req
        field_data = field_data[0]
        if field_data.content_type != 'image/jpeg':
            raise ValueError
        if field_name == 't1_cover':
            path = os.path.join(temp_dir_name, 'cover.jpg')
        elif field_name.startswith('t1_central'):
            cental_num = field_name.split('|')[-1]
            path = os.path.join(temp_dir_name, f'final.cent.{cental_num}.jpg')
        elif field_name == 't1_float_left':
            path = os.path.join(temp_dir_name, 'final.left.jpg')
        elif field_name == 't1_float_right':
            path = os.path.join(temp_dir_name, 'final.right.jpg')
        elif field_name.startswith('t1_shot'):
            shot_num = field_name.split('|')[-1]
            after_before_state = field_name.split('|')[-2]
            path = os.path.join(temp_dir_name, f'shot.{after_before_state}.{shot_num}.jpg')
        field_data.save(path)

    zip_file = zipfile.ZipFile(os.path.join(temp_dir_name, zip_name), 'w')
    for root, dirs, files in os.walk(temp_dir_name):
        for file in files:
            if file != zip_name:
                zip_file.write(os.path.join(root, file), arcname=file)


@logger.catch
@app_route.route('/long_tile', methods=['POST'])
def long_tile():
    try:
        long_jpg = connectors.graphic.get_long_tile_jpg(
            request.files.getlist('forLongTile'),
            request.form.get('width'),
            request.form.get('schema'),
            request.form.get('border'),
            request.form.get('border_color'),
        )
    except Exception as e:
        logger.error(e.args)
        return
    return send_file(long_jpg, mimetype='image/jpeg')