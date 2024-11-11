import asyncio
from asyncio import sleep

import settings
import requests

user = settings.monetag_user
password = settings.monetag_pass
origin = settings.web_url
monetag_key = settings.monetag_key
async def monetag():
    global origin
    global password
    global user
    global monetag_key
    url = origin
    while True:
        try:
            with open('monetag_token.txt', 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            token = None
        is_token_valid = True

        if token:
            balance_url = "https://publishers.monetag.com/api/client/balance/"
            balance_headers = {
                'Authorization': f'Bearer {token}',  # Include the token in the headers
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.7',
                'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
                'x-ssp-language': 'en'
            }
            balance_response = requests.get(balance_url, headers=balance_headers)

            if balance_response.status_code == 200:
                print("Balance information:", balance_response.json())
                # Logged in successfully
                total_balance = balance_response.json().get('payout_balance') + balance_response.json().get('hold_earning') + balance_response.json().get('total_withdraws')
                print("Total balance:", total_balance)
                # Send post request to the server to update the balance, api_url = url+'/adupdate'
                adupdate_payload = {
                    "key": monetag_key,
                    "total_usd": total_balance
                }
                adupdate_response = requests.post(url+'/adupdate', json=adupdate_payload)
                if adupdate_response.status_code == 200:
                    print("Balance updated successfully")
                    print("Response:", adupdate_response.text)
                else:
                    print("Balance update failed. Status Code:", adupdate_response.status_code)
                    print("Response:", adupdate_response.text)
            else:
                is_token_valid = False
        else:
            is_token_valid = False

        if not is_token_valid:
            login_url = "https://publishers.monetag.com/api/client/public/login/"
            login_payload = {
                "username": user,
                "password": password,
                "type": "publisher",
                "partner_alias": "propeller",
                "fingerprint": "d25544e32b71e579bcfc79dbd65f8bb8",
                "captcha": ""
            }
            headers = {
                'Content-Type': 'application/json'
            }

            login_response = requests.post(login_url, json=login_payload, headers=headers)
            if login_response.status_code == 200:
                token = login_response.json().get('api_token')
                # Update the token in monetag_token.json
                with open('monetag_token.txt', 'w') as f:
                    f.write(token)
                
            else:
                print("Login failed. Status Code:", login_response.status_code)
                print("Response:", login_response.json())
                await sleep(10)
        else:
            await sleep(600)


async def catbox():
    global origin
    while True:
        try:
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
            await sleep(10)
        await sleep(60)


async def main():
    await asyncio.gather(monetag(), catbox())

if __name__ == "__main__":
    asyncio.run(main())