import requests
import time
#http://127.0.0.1:5000/static/videos/Rhla4.mp4
while True:
    try:
        origin = "localhost:5000"
        url = origin + "/catupload"
        response = requests.get(url)
        if response.status_code == 200:
            if response.text == "NULL":
                print("No video to upload")
            else:
                filename = response.text
                data = {"type": "accepted", "name": filename}
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    if response.text == "sending":
                        print("Video sending to catbox")
                        video_path = origin + f"/static/videos/{filename}"
                        files = {
                            'reqtype': (None, 'urlupload'),
                            'userhash': (None, "da98f6c298dce1186854a1bfe"),
                            'url':(None,video_path) #video_path
                        }
                        response = requests.post('https://catbox.moe/user/api.php', files=files)
                        if response.status_code == 200:
                            print("Video uploaded")
                            print(video_path, " link attached to: ",response.text)
                            data = {"type": "done", "name": filename, "url": response.text}
                            response = requests.post(url, json=data)
                            if response.status_code == 200:
                                if response.text == "added":
                                    print("Video added to the database")
                                else:
                                    print("Error:", response.text)
                            else:
                                print("Error:", response.status_code)
                        else:
                            print("Error:", response.text)
                    else:
                        print("Error:", response.text)
                else:
                    print("Error:", response.status_code)
        else:
            print("Error:", response.status_code)
    except Exception as e:
        print("Error:", e)
    time.sleep(60)