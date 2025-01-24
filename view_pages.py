import string
from flask import current_app, Blueprint, flash, render_template, request, redirect, url_for, render_template_string
import random
import os

from flask_login import current_user, login_required
from . import db
from .models import Base, User, Last_access
from .settings import monetag_key
from .viewers import distribute
current_directory = os.getcwd()
items = os.listdir(current_directory)
if 'VideoBin' in items:
    os.chdir(current_directory+'/VideoBin')


view_pages = Blueprint('view_pages', __name__)



@view_pages.route('/')
def index():
    return render_template('home.html')
@view_pages.route('/upload-policy')
def policy():
    return render_template('policy.html')
@view_pages.route('/archive')
def archive():
    if current_user.is_authenticated == False:
        return render_template('archive.html')
    
    user = db.session.get(User, current_user.id)
    urls = user.bases

    return render_template('archive.html', urls=urls)

@view_pages.route('/profile')
@login_required
def profile():
    user = db.session.query(User).filter_by(id=current_user.id).first()
    logs = user.distribution_logs
    return render_template('profile.html', name=current_user.name, wallet = current_user.wallet, logs=logs)

@view_pages.route('/m/<prefix>')
def show_entries(prefix):
    prefix_info = db.session.get(Base, prefix)
    if not prefix_info or prefix_info.link_type != 1:
        return f'Invalid URL'
    entries = Base.query.filter(Base.baseurl.like(f'{prefix}%')).all()
    return render_template('show_entries.html', prefix = prefix_info, entries=entries)

@view_pages.route('/edit_video/<prefix>')
@login_required
def edit(prefix):
    prefix_info = db.session.query(Base).filter_by(baseurl=prefix, user_id=current_user.id).first()
    if not prefix_info:
        return f'Invalid URL'
    return render_template('edit.html', prefix = prefix_info)


@view_pages.route('/edit_video/<prefix>', methods=['POST'])
@login_required
def edit_post(prefix):
    action = request.form.get('action')
    prefix_info = db.session.query(Base).filter_by(baseurl=prefix, user_id=current_user.id).first()
    if action == 'delete':
        if prefix_info:
            try:
                db.session.query(Base).filter_by(baseurl=prefix).delete()
                db.session.commit()
                #flash('Video deleted successfully!', 'success')
                return redirect(url_for('view_pages.archive'))
            except Exception as e:
                db.session.rollback()
                #flash(f'An error occurred while deleting the video: {str(e)}', 'danger')
                return redirect(url_for('view_pages.edit', prefix=prefix))
        else:
            #flash('Video not found or you don’t have permission to delete it.', 'danger')
            return redirect(url_for('view_pages.edit', prefix=prefix))
    elif action == 'change':
        if not prefix_info:
            return f'Invalid URL'
        prefix_info.name = request.form.get('newName', prefix_info.name)
        prefix_info.ad_percent = request.form.get('percent', prefix_info.ad_percent)
        db.session.commit()
        return redirect(url_for('view_videos.view_video', filename=prefix))

@view_pages.route('/adupdate', methods=['POST'])
def adupdate():
    req = request.json
    key = req['key']
    total_usd = float(req['total_usd'])
    time_now = db.func.current_timestamp()
    if key == monetag_key:
        old_data = db.session.get(Last_access, 1)
        if not old_data:
            success = distribute(0, total_usd)
            if not success:
                return "False"
            new_data = Last_access(access_type=1, access_time=time_now, value=str(total_usd))
            db.session.add(new_data)
            db.session.commit()
            return "True"
        elif abs(total_usd - float(old_data.value)) > 0.01:
            success = distribute(float(old_data.value), total_usd)
            if not success:
                return "False"
            old_data.access_time = time_now
            old_data.value = str(total_usd)
            db.session.commit()
            return "True"
        else:
            return "No Change"
    else:
        return "False"