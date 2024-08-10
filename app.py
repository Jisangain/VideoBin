import random
import string
from flask import Flask, render_template, render_template_string, request, redirect, url_for
from flask import jsonify
import json
import os
from random import randint
import time
app = Flask(__name__)
app.secret_key = 'udsgoyfundgofcyadspijhorfaisgfsai8dygpd'
UPLOAD_FOLDER = 'static/videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

data = {}

with open('shortenlink.json', 'r') as file:
    data = json.load(file)
def write_shorturl(key, value, filename='shortenlink.json'):
    global data
    data[key] = value
    with open('shortenlink.json', 'w') as file:
        json.dump(data, file, indent=4)

adinfo = {}
with open('adinfo.json', 'r') as file:
    adinfo = json.load(file)
def write_adinfo(key, value, filename='adinfo.json'):
    global adinfo
    adinfo[key] = value
    with open('adinfo.json', 'w') as file:
        json.dump(adinfo, file, indent=4)


track_uses = {} # {time: [(filename, count), (filename, count),...], time: [(filename, count), (filename, count),...], ...}
with open('track_uses.json', 'r') as file:
    track_uses = json.load(file)
def write_track(latest_track, filename='track_uses.json'):
    with open('track_uses.json', 'w') as file:
        json.dump(latest_track, file, indent=4)



upload_status = {} # {filename: status, filename: status, ...}
# http://127.0.0.1:5000/static/videos/Rhla4.mp4
# Route to render the upload form
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
                    
            if change_ad_script == False:
                write_adinfo(random_filename[:-4], {'is_public':make_public, 'change_ad_script': change_ad_script})
            elif ad_option == "minimal":
                write_adinfo(random_filename[:-4], {'is_public':make_public, 'change_ad_script': change_ad_script, 'ad_option': ad_option})
            else:
                write_adinfo(random_filename[:-4], {'is_public':make_public, 'change_ad_script': change_ad_script, 'ad_option': ad_option, 'ad_script': ad_script, 'ad_position': ad_position})
            
            video_url = url_for('view_video', filename=random_filename)
            
            write_shorturl(random_filename[:-4], "/static/videos/"+random_filename)
            return video_url

    return render_template('upload2.html')

@app.route('/catupload', methods=['POST', 'GET'])
def UploadStatus():
    print(upload_status)
    if request.method == 'POST':
        req = request.json
        request_type = req['type']
        if request_type == 'check':
            for key in upload_status:
                if upload_status[key] == 'uploaded':
                    return key
            return "NULL"
        if request_type == 'accepted':
            name = req['name']
            upload_status[name] = 'sending'
            return 'sending'
        if request_type == 'done':
            name = req['name']
            new_url = req['url']
            write_shorturl(name[:-4], new_url)
            os.remove(os.path.join('static/videos', name))
            del upload_status[name]
            return 'added'
    return "Invalid request", 400



@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload-policy')
def policy():
    return render_template('policy.html')

@app.route('/archive')
def archive():
    sorted_data = dict(sorted(data.items()))
    return render_template('archive.html', sorted_data=sorted_data)

@app.route('/v')
def nothing():
    return redirect('/v/nothing')


track_time = 3*60*60 # 3 hours, remove all time entries older than this
track_interval = 10*60 # 10 minutes, how often add a new time entry and remove old ones
last_track = time.time()  # last time a new time entry was added
recent_tracks = {} # {filename: count, filename: count, ...}

@app.route('/add', methods=['GET', 'POST'])
def addurl():
    if request.method == 'POST':
        user_input = request.form['user_input']
        if "http" in user_input:
            # generate 5 random characters
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            write_shorturl(random_string, user_input)
            return redirect('/v/' + random_string + ".mp4")
    return render_template_string('''
        <!doctype html>
        <title>Input Form</title>
        <h1>Enter your text</h1>
        <form method=post>
          <input type=text name=user_input>
          <input type=submit value=Submit>
        </form>
    ''')



@app.route('/v/<filename>')
def view_video(filename):

    global track_uses
    global track_time
    global track_interval
    global last_track
    global recent_tracks
    global data
    redirecttype = False
    if filename[-4:] == ".mp4":
        filename = filename[:-4]
        redirecttype = True
    if filename not in data or filename == "nothing":
        print("a")
        return render_template('player2.html', selected_video="/static/nothing")

    if filename in recent_tracks:
        recent_tracks[filename] += 1
    else:
        recent_tracks[filename] = 1

    if time.time() - last_track > track_interval:
        timenow = time.time()
        track_uses[timenow] = []
        for key in recent_tracks:
            track_uses[timenow].append((key, recent_tracks[key]))
        recent_tracks = {}
        for key in list(track_uses.keys()):
            if timenow - float(key) > track_time:
                del track_uses[key]
        write_track(track_uses)



    if redirecttype == True:
        actual_link = data[filename]
        info = adinfo[filename]
        if info['change_ad_script'] == True:
            rand = randint(0, 100)
            if info['ad_option'] == "minimal":
                if rand<5:
                    return render_template('player.html', selected_video=actual_link)
                else:
                    return render_template('player_custom.html', selected_video=actual_link, ad_script="", ad_position="")
            elif info['ad_option'] == "custom":
                if rand<5:
                    return render_template('player.html', selected_video=actual_link)
                else:
                    if info['ad_position'] == "head":
                        return render_template('player_custom.html', selected_video=actual_link, headscript=info['ad_script'], bodyscript="")
                    elif info['ad_position'] == "body":
                        return render_template('player_custom.html', selected_video=actual_link, headscript="", bodyscript=info['ad_script'])
        return render_template('player.html', selected_video=actual_link)

    if time.time() - last_track > track_interval:
        last_track = time.time()
        top_10 = {}
        for key in track_uses:
            for filename, count in track_uses[key]:
                if filename in top_10:
                    top_10[filename] += count
                else:
                    top_10[filename] = count
        top_10 = dict(sorted(top_10.items(), key=lambda x: x[1], reverse=True)[:10])


    actual_link = data[filename]
    return render_template('player2.html', selected_video=actual_link)




if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
