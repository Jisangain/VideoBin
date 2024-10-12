import string
from flask import current_app, Blueprint, render_template, request, redirect, url_for, render_template_string
import random
import os
from random import randint
from . import db, upload_status
from .models import Base

current_directory = os.getcwd()
items = os.listdir(current_directory)
if 'VideoBin' in items:
    os.chdir(current_directory+'/VideoBin')


uploadview = Blueprint('uploadview', __name__)


def insert_data(baseurl, mainurl, make_public = 0, link_type = 0, name = '', user = 1):
    new_entry = Base(baseurl=baseurl, mainurl=mainurl, make_public=make_public, link_type=link_type, name=name, user=user)
    db.session.add(new_entry)
    db.session.commit()

def get_single_data(baseurl):
    return db.session.get(Base, baseurl)


@uploadview.route('/m/<prefix>')
def show_entries(prefix):
    prefix_info = get_single_data(prefix)
    if not prefix_info or prefix_info.link_type != 1:
        return f'Invalid URL'
    entries = Base.query.filter(Base.baseurl.like(f'{prefix}%')).all()
    return render_template('show_entries.html', prefix = prefix_info, entries=entries)

@uploadview.route('/v/<filename>')
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
    if redirecttype == True:
        #if video_info.change_ad_script == False:
        return render_template('player.html', selected_video=actual_link)
        """if video_info.change_ad_script == True:
            rand = randint(0, 100)
            if video_info.ad_option == 0:
                if rand<5:
                    return render_template('player.html', selected_video=actual_link)
                else:
                    return render_template('player_custom.html', selected_video=actual_link, ad_script="", ad_position="")
            elif video_info.ad_option == 1:
                if rand<5:
                    return render_template('player.html', selected_video=actual_link)
                else:
                    if video_info.position == 1:
                        return render_template('player_custom.html', selected_video=actual_link, headscript=video_info.ad_script, bodyscript="")
                    elif video_info.position == 0:
                        return render_template('player_custom.html', selected_video=actual_link, headscript="", bodyscript=video_info.ad_script)
        return render_template('player.html', selected_video=actual_link)"""
    return render_template('player2.html', selected_video=actual_link)


@uploadview.route('/')
def index():
    return render_template('home.html')
@uploadview.route('/upload-policy')
def policy():
    return render_template('policy.html')
@uploadview.route('/archive')
def archive():
    urls = Base.query.with_entities(Base.name, Base.baseurl).filter_by(link_type=1).all()
    return render_template('archive.html', urls=urls)