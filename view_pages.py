import string
from flask import current_app, Blueprint, render_template, request, redirect, url_for, render_template_string
import random
import os

from flask_login import current_user, login_required
from . import db
from .models import Base

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
    urls = Base.query.with_entities(Base.name, Base.baseurl).filter_by(link_type=1).all()
    return render_template('archive.html', urls=urls)

@view_pages.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)