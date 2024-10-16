import string
from flask import current_app, Blueprint, render_template, request, redirect, url_for, render_template_string
import random
import os

from flask_login import current_user, login_required
from . import db
from .models import Base, User

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
    return render_template('profile.html', name=current_user.name, wallet = current_user.btc_address, logs=logs)

@view_pages.route('/m/<prefix>')
def show_entries(prefix):
    prefix_info = db.session.get(Base, prefix)
    if not prefix_info or prefix_info.link_type != 1:
        return f'Invalid URL'
    entries = Base.query.filter(Base.baseurl.like(f'{prefix}%')).all()
    return render_template('show_entries.html', prefix = prefix_info, entries=entries)