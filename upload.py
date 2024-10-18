import string
from flask import current_app, Blueprint, render_template, request, redirect, url_for, render_template_string
import random
import os

from flask_login import current_user
from . import db, upload_status
from .models import Base

current_directory = os.getcwd()
items = os.listdir(current_directory)
if 'VideoBin' in items:
    os.chdir(current_directory+'/VideoBin')


upload = Blueprint('upload', __name__)


def insert_data(baseurl, mainurl, make_public = 0, link_type = 0, name = '', user_id = 1, ad_percent = 50):
    new_entry = Base(baseurl=baseurl, mainurl=mainurl, make_public=make_public, link_type=link_type, name=name, user_id=user_id, ad_percent=ad_percent)
    db.session.add(new_entry)
    db.session.commit()


def get_single_data(baseurl):
    return db.session.get(Base, baseurl)


@upload.route('/catupload', methods=['POST', 'GET'])
def UploadStatus():
    if request.method == 'GET':
        for key in upload_status:
            if upload_status[key] == 'uploaded' or upload_status[key] == 'sending':
                return key
        return "NULL"
    elif request.method == 'POST':
        req = request.json

        request_type = req['type']
        name = req['name']

        if request_type == 'accepted' and name in upload_status:
            upload_status[name] = 'sending'
            return 'sending'
        if request_type == 'done' and name in upload_status:
            new_url = req['url']
            base_entry = db.session.get(Base, name[:-4])
            if base_entry:
                base_entry.mainurl = new_url
                db.session.commit()
                os.remove(os.path.join('static/videos', name))
                del upload_status[name]
                return 'added'
            return 'added'
    return "Invalid request", 400

@upload.route('/upload', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        video = request.files['video']
        percent = request.form.get('percent', 50)

        if video and video.filename.endswith('.mp4'):
            random_filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '.mp4'
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], random_filename)

            
            video.save(video_path)
            upload_status[random_filename] = 'uploaded'            
            video_url = url_for('view_videos.view_video', filename=random_filename)
            user_id = 1
            if current_user.is_authenticated:
                user_id = current_user.id
            insert_data(random_filename[:-4], '/static/videos/'+random_filename, ad_percent=percent, user_id=user_id)
            return video_url[:-4]
    return render_template('upload.html')

@upload.route('/newvideolist', methods=['GET', 'POST'])
def newvideolist():
    if request.method == 'POST':
        random_filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
        name = request.form.get('name', random_filename)
        make_public = 'make_public' in request.form

        insert_data(random_filename, '/m/' + random_filename, make_public, name=name, link_type=1)
        return redirect("/edit/"+random_filename)

    return render_template('newvideolist.html')


@upload.route('/edit/<prefix>', methods=['GET', 'POST'])
def add_entry(prefix):
    prefix_info = get_single_data(prefix)
    if not prefix_info or prefix_info.link_type != 1:
        return f'Invalid URL'
    if request.method == 'POST':

        video = request.files['video']
        if video and video.filename.endswith('.mp4'):
            last_entry = Base.query.filter(Base.baseurl.like(f'{prefix}%')).order_by(Base.baseurl.desc()).first()
            if last_entry:
                if len(last_entry.baseurl[len(prefix):]) == 0:
                    last_number = 0
                else:
                    last_number = int(last_entry.baseurl[len(prefix):])
                new_number = last_number + 1
            else:
                new_number = 0
            new_baseurl = f'{prefix}{new_number:03}'

            random_filename = new_baseurl + '.mp4'
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], random_filename)
            insert_data(new_baseurl, "/static/videos/"+random_filename)
            video.save(video_path)
            upload_status[random_filename] = 'uploaded'
            video_url = url_for('upload.view_video', filename=random_filename)            
            return video_url
        else:
            return 'Invalid file'
    return render_template('upload2.html', name=prefix_info.name, prefix=prefix)



@upload.route('/submit_link', methods=['POST'])
def addurl():
    video_link = request.form.get('videoLink', '')
    percent = request.form.get('percent', 50)

    if "http" in video_link and video_link.endswith('.mp4'):
        random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        video_url = url_for('view_videos.view_video', filename=random_filename)
        user_id = 1
        if current_user.is_authenticated:
            user_id = current_user.id
        insert_data(random_filename, video_link, ad_percent=percent, user_id=user_id)
        return video_url
    return render_template('upload.html')


