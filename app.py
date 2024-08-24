import string
from flask import Flask, render_template, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
import random
import os
from random import randint
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:pass@localhost/flaskapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
app.config['UPLOAD_FOLDER'] = 'static/videos'

db = SQLAlchemy(app)



class Base(db.Model):
    baseurl = db.Column(db.String(80), primary_key=True)
    mainurl = db.Column(db.String(80), nullable=False)
    make_public = db.Column(db.Boolean, nullable=False)
    change_ad_script = db.Column(db.Boolean, nullable=False)
    link_type = db.Column(db.Integer, nullable=False)

    name = db.Column(db.String(80))
    ad_option = db.Column(db.Boolean)
    ad_script = db.Column(db.String(300))
    position = db.Column(db.Integer)
    count = db.Column(db.Integer)
    user = db.Column(db.String(80))
    def __repr__(self):
        return f'<Base {self.baseurl}>'

# Add data to table
def insert_data(baseurl, mainurl, make_public = 0, change_ad_script = 0, link_type = 0, name = '', ad_option = 0, ad_script = '', position = 0):
    new_entry = Base(baseurl=baseurl, mainurl=mainurl, make_public=make_public,
                     change_ad_script=change_ad_script, link_type=link_type, name=name, ad_option=ad_option,
                     ad_script=ad_script, position=position)
    db.session.add(new_entry)
    db.session.commit()

# Get single data
def get_single_data(baseurl):
    return db.session.get(Base, baseurl)

upload_status = {}

with app.app_context():
    upload_status = {}
    local_urls = Base.query.filter(Base.mainurl.like(f'{"/static/videos/"}%')).all()
    for url in local_urls:
        upload_status[url.baseurl + '.mp4'] = 'uploaded'

@app.route('/catupload', methods=['POST', 'GET'])
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
            base_entry = Base.query.get(name[:-4])
            if base_entry:
                base_entry.mainurl = new_url
                db.session.commit()
                os.remove(os.path.join('static/videos', name))
                del upload_status[name]
                return 'added'
            return 'added'
    return "Invalid request", 400

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        video = request.files['video']
        make_public = 'make_public' in request.form
        change_ad_script = 'change_ad_script' in request.form
        ad_option = request.form.get('ad_option', '')
        ad_script = request.form.get('ad_script', '')
        ad_position = request.form.get('ad_position', '')

        if video and video.filename.endswith('.mp4'):
            random_filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '.mp4'
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
            video.save(video_path)
            upload_status[random_filename] = 'uploaded'
            if ad_option == "custom":
                ad_script = ad_script.strip()
                if len(ad_script)<=100 and ad_script.startswith("<script>") and ad_script.endswith("</script>") and ad_script.count("script") == 2:
                    ad_script = ad_script[8:-9]
                else:
                    change_ad_script = False

            #random_filename[:-4]
            if change_ad_script == False:
                insert_data(random_filename[:-4], '/static/videos/'+random_filename, make_public, change_ad_script)
            elif ad_option == "minimal":
                insert_data(random_filename[:-4], '/static/videos/'+random_filename, make_public, change_ad_script, 0, '', 0)
            else:
                insert_data(random_filename[:-4], '/static/videos/'+random_filename, make_public, change_ad_script, 0, '', 1, ad_script, ad_position)

            video_url = url_for('view_video', filename=random_filename)
            return video_url

    return render_template('upload.html')

@app.route('/newvideolist', methods=['GET', 'POST'])
def newvideolist():
    if request.method == 'POST':
        random_filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
        name = request.form.get('name', random_filename)
        make_public = 'make_public' in request.form
        change_ad_script = 'change_ad_script' in request.form
        ad_option = request.form.get('ad_option', '')
        ad_script = request.form.get('ad_script', '')
        ad_position = request.form.get('ad_position', '')


        if ad_option == "custom":
            ad_option = 1
            ad_script = ad_script.strip()
            if len(ad_script)<=100 and ad_script.startswith("<script>") and ad_script.endswith("</script>") and ad_script.count("script") == 2:
                ad_script = ad_script[8:-9]
            else:
                ad_script = ''
                change_ad_script = False
        else:
            ad_option = 0
        if ad_position == "body":
            ad_position = 0
        else:
            ad_position = 1

        insert_data(random_filename, '/m/' + random_filename, make_public, change_ad_script, 1, name, ad_option, ad_script, ad_position)
        print(name, make_public, change_ad_script, ad_option, ad_script, ad_position)
        return redirect("/edit/"+random_filename)

    return render_template('newvideolist.html')

@app.route('/m/<prefix>')
def show_entries(prefix):
    prefix_info = get_single_data(prefix)
    if not prefix_info or prefix_info.link_type != 1:
        return f'Invalid URL'
    entries = Base.query.filter(Base.baseurl.like(f'{prefix}%')).all()
    return render_template('show_entries.html', prefix = prefix_info, entries=entries)

@app.route('/edit/<prefix>', methods=['GET', 'POST'])
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
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
            video.save(video_path)
            upload_status[random_filename] = 'uploaded'
            video_url = url_for('view_video', filename=random_filename)
            insert_data(new_baseurl, "/static/videos/"+random_filename)
            return video_url
        else:
            return 'Invalid file'
    return render_template('upload2.html', name=prefix_info.name, prefix=prefix)

@app.route('/v/<filename>')
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
        if video_info.change_ad_script == False:
            return render_template('player.html', selected_video=actual_link)
        if video_info.change_ad_script == True:
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
        return render_template('player.html', selected_video=actual_link)
    return render_template('player2.html', selected_video=actual_link)

@app.route('/add', methods=['GET', 'POST'])
def addurl():
    if request.method == 'POST':
        user_input = request.form['user_input']
        if "http" in user_input and user_input.endswith('.mp4'):
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            insert_data(random_string, user_input)
            return redirect('/v/' + random_string + ".mp4")
        else:
            return "Invalid URL. Please provide a valid URL ending with '.mp4'."
    return render_template_string('''
        <!doctype html>
        <title>Input Form</title>
        <h1>Enter your text</h1>
        <form method=post>
          <input type=text name=user_input>
          <input type=submit value=Submit>
        </form>
    ''')

@app.route('/')
def index():
    return render_template('home.html')
@app.route('/upload-policy')
def policy():
    return render_template('policy.html')
@app.route('/archive')
def archive():
    urls = Base.query.with_entities(Base.name, Base.baseurl).filter_by(link_type=1).all()
    return render_template('archive.html', urls=urls)
if __name__ == '__main__':
    app.run(debug=True)