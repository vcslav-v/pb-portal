import os
import shutil
import zipfile
from datetime import datetime

from flask import (Blueprint, Response, flash, redirect, render_template,
                   request, send_file, url_for)
from loguru import logger
from pydantic import ValidationError

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
        connectors.graphic.get_tiny_zip(
            request.form.get('prefix'),
            request.form.get('resize_width'),
            True if request.form.get('is_tinify') == 'true' else False,
        )
    except Exception as e:
        logger.error(e.args)
        return
    return 'ok'


@logger.catch
@app_route.route('/longy', methods=['POST'])
def longy():
    try:
        connectors.graphic.get_long_jpg(
            int(request.form.get('num_files')),
            request.form.get('width'),
            request.form.get('height'),
            request.form.get('n_cols'),
            request.form.get('prefix'),
        )
    except Exception as e:
        logger.error(e.args)
        return
    return 'ok'


@logger.catch
@app_route.route('/cutter', methods=['POST'])
def cutter():
    try:
        connectors.graphic.cut_pics(
            int(request.form.get('left')) if request.form.get('left') else 0,
            int(request.form.get('top')) if request.form.get('top') else 0,
            int(request.form.get('right')) if request.form.get('right') else 0,
            int(request.form.get('bottom')) if request.form.get('bottom') else 0,
            request.form.get('prefix'),
        )
    except Exception as e:
        logger.error(e.args)
        return
    return 'ok'


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
@app_route.route('/get_utm_info', methods=['GET'])
def get_utm_info():
    return connectors.link_dealer.get_info().model_dump_json()


@logger.catch
@app_route.route('/get_utm', methods=['POST'])
def get_utm():
    data = connectors.link_dealer.schemas.LinkCreate(
        target_url=request.form.get('target_url'),
        source=int(request.form.get('source')),
        medium=int(request.form.get('medium')),
        campaign_project=int(request.form.get('campaign_project')),
        term_material=int(request.form.get('term_material')),
        term_page=int(request.form.get('term_page')),
        user=int(request.form.get('user')),
    )
    if request.form.get('campaning_dop'):
        data.campaning_dop = request.form.get('campaning_dop')
    if request.form.get('content'):
        data.content = int(request.form.get('content'))
    return connectors.link_dealer.get_utm(data).model_dump_json()


@logger.catch
@app_route.route('/get_last_utms', methods=['GET'])
def get_last_utms():
    return connectors.link_dealer.get_last_utms().model_dump_json()


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
        connectors.graphic.get_long_tile_jpg(
            int(request.form.get('num_files')),
            request.form.get('width'),
            request.form.get('schema'),
            request.form.get('border'),
            request.form.get('border_color'),
            request.form.get('prefix'),
        )
    except Exception as e:
        logger.error(e.args)
        return
    return 'ok'


@logger.catch
@app_route.route('/prepare_s3_url', methods=['GET'])
def prepare_s3_url():
    filename = request.args.get('filename')
    content_type = request.args.get('content_type')
    prefix = request.args.get('prefix')
    try:
        result = connectors.graphic.make_s3_url(
            filename,
            content_type,
            prefix,
        )
    except Exception as e:
        logger.error(e.args)
        return
    return result


@logger.catch
@app_route.route('/long_tile_check', methods=['POST'])
def long_tile_check():
    logger.debug('check long tile')
    long_jpg = connectors.graphic.long_tile_check(
        request.form.get('prefix'),
    )
    return long_jpg


@logger.catch
@app_route.route('/cutter_check', methods=['POST'])
def cutter_check():
    logger.debug('check long tile')
    pic_zip = connectors.graphic.cutter_check(
        request.form.get('prefix'),
    )
    return pic_zip


@logger.catch
@app_route.route('/tiny_check', methods=['POST'])
def tiny_check():
    logger.debug('check tiny')
    tiny_zip = connectors.graphic.tiny_check(
        request.form.get('prefix'),
    )
    return tiny_zip


@logger.catch
@app_route.route('/utmer', methods=['GET', 'POST'])
def utmer():
    return render_template(
            'utmer.html',
        )


@logger.catch
@app_route.route('/get_utm_html', methods=['POST'])
def get_utm_html():
    data = connectors.mailer.schemas.HTML_with_UTM(
        html=request.form.get('html'),
        campaign_project=int(request.form.get('project')),
        campaning_dop=request.form.get('campaign_name'),
    )
    result = connectors.mailer.html_with_utm(data)
    return result.model_dump_json()
