from flask import Blueprint, render_template
import os
from . import db
from .models import Base, countlog
from random import randint

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
    log = db.session.get(countlog, video_info.user_id)
    if log:
        log.viewcount += 1
    else:
        log = countlog(user_id=video_info.user_id, viewcount=1)

    db.session.add(log)
    db.session.commit()

    random = randint(1, 100)
    ad = video_info.ad_percent >= random
    if redirecttype == True:
        return render_template('player.html', selected_video=actual_link, ad = ad)
    else:
        return render_template('player2.html', selected_video=actual_link, ad = ad)