from flask import Blueprint, render_template, request
from sqlalchemy.sql import text
import os
from . import db, upload_status
from .models import Base, countlog
from random import randint
from .settings import self_ad
from flask_login import current_user
from .viewers import distribute, is_a_new_viewer

current_directory = os.getcwd()
items = os.listdir(current_directory)
if 'VideoBin' in items:
    os.chdir(current_directory+'/VideoBin')


view_videos = Blueprint('view_videos', __name__)


def get_single_data(baseurl):
    return db.session.get(Base, baseurl)


@view_videos.route('/v/<filename>')
def view_video(filename):
    redirecttype = False
    if filename[-4:] == ".mp4":
        filename = filename[:-4]
        redirecttype = True
    video = get_single_data(filename)
    if not video:
        return f'Invalid URL'
    video_info = get_single_data(filename[:-3])
    if not video_info:
        video_info = video

    actual_link = video.mainurl


    random = randint(1, 100)
    ad = video_info.ad_percent >= random
    if current_user.is_authenticated and current_user.id == video_info.user_id:
        ad = False
    if ad:
        user_id = video_info.user_id
        if randint(0,99)<self_ad:
            user_id = 1
        # Check if the viewers ip is_a_new_viewer is true
        ip = request.headers.get('X-Real-IP')
        if ip is None:
            ip = request.remote_addr

        if is_a_new_viewer(ip):
            db.session.execute(
                text("""
                    INSERT INTO countlog (user_id, viewcount) 
                    VALUES (:user_id, 1)
                    ON DUPLICATE KEY UPDATE viewcount = viewcount + 1
                """),
                {"user_id": user_id}
            )
            db.session.commit()
    if redirecttype == True:
        return render_template('player.html', selected_video=actual_link, ad = ad)
    else:
        return render_template('player2.html', selected_video=actual_link, ad = ad, video_info = video_info)