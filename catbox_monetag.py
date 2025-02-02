import asyncio
from asyncio import sleep
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import json
import hmac
import hashlib
import settings
import time

user = settings.monetag_user
password = settings.monetag_pass
web_url = settings.web_url
connector_key = settings.connector_key
binance_api = settings.binance_api
binance_secret = settings.binance_secret


async def monetag():
    global web_url
    global password
    global user
    global connector_key
    url = web_url
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
                    "key": connector_key,
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
    global web_url
    while True:
        try:
            url = web_url + "/catupload"
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
                            video_path = web_url + f"/static/videos/{filename}"
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







key = RSA.generate(3072)
private_key = key
public_key = key.publickey()
cipher = PKCS1_OAEP.new(private_key)



def send_public_key():
    public_key_pem = public_key.export_key().decode('utf-8')
    requests.post(f'{web_url}/send_key', json={'public_key': public_key_pem})

def get_encrypted_data():
    response = requests.get(f'{web_url}/withdraw_request')
    if response.status_code == 200:
        data = response.json()
        encrypted_data = bytes.fromhex(data['encrypted_data'])
        return encrypted_data
    elif response.status_code == 220:
        return "just_wait"
    else:
        return None

def decrypt_and_verify(encrypted_data):
    global cipher
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
    except ValueError as e:
        if str(e) == 'Incorrect decryption.':
            send_public_key()
            return 'New key sent', 0
        else:
            return f'Error: {e}', -1
    except Exception as e:
        return f'Error: {e}', -1
    return decrypted_data.decode('utf-8'), 1


def submit_withdrawal(withdrawOrderId, address, amount, network):
    url = f'https://api.binance.com/sapi/v1/capital/withdraw/apply'
    
    # Parameters
    params = {
        'coin': "USDT",
        'withdrawOrderId': withdrawOrderId,
        'address': address,
        'amount': float(amount),
        'network': network,
        'transactionFeeFlag': 'true',
        'timestamp': int(time.time() * 1000)
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(
        binance_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    params['signature'] = signature
    
    headers = {
        'X-MBX-APIKEY': binance_api
    }
    
    # Send request
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        return "Withdrawal submitted successfully!", 1
    else:
        return response.json(), 0



def get_withdrawal_status(withdrawOrderId):
    url = f'https://api.binance.com/sapi/v1/capital/withdraw/history'
    params = {
        'withdrawOrderId': withdrawOrderId,
        'timestamp': int(time.time() * 1000)
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(
        binance_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    params['signature'] = signature

    headers = {
        'X-MBX-APIKEY': binance_api
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for withdrawal in data:
            if withdrawal['withdrawOrderId'] == withdrawOrderId:
                return withdrawal['withdrawOrderId'], 1
        return "Withdrawal not found.", 0
    else:
        return f"Error: {response.status_code} - {response.json()}", -1



async def payout():
    while True:
        encrypted_data = get_encrypted_data()
        if encrypted_data == 'just_wait':
            await sleep(60)
            continue
        if encrypted_data:
            data = decrypt_and_verify(encrypted_data)
            if data[1] == 0: # New key to send
                send_public_key()
                await sleep(10)
                continue
            elif data[1] == -1: # Some error while decrypting
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {data[0]}')
            else:
                data = json.loads(data[0])
                status = get_withdrawal_status(data['withdrawal_id'])

                if status[1] == 1: # Privious withdrawal found
                    to_send = {
                        'id': data['id'],
                        'withdrawal_id': data['withdrawal_id'],
                        'user_id': data['user_id'],
                        'success': True
                    }
                    response = requests.post(f'{web_url}/withdraw_update', json=to_send)
                    print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - Old withdrawal found')
                elif status[1] == 0: # Need to submit withdrawal
                    status = submit_withdrawal(data['withdrawal_id'], data['address'], data['amount'], data['network'])
                    if status[1] == 1:
                        to_send = {
                            'id': data['id'],
                            'withdrawal_id': data['withdrawal_id'],
                            'user_id': data['user_id'],
                            'success': True
                        }
                        response = requests.post(f'{web_url}/withdraw_update', json=to_send)
                        print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - Done: {status[0]}')
                    else:
                        to_send = {}
                        if status[0]['code'] == -4026:
                            to_send = {
                                'id': data['id'],
                                'withdrawal_id': data['withdrawal_id'],
                                'user_id': data['user_id'],
                                'success': False,
                                'reason': 'Insufficient server funds'
                            }
                            print(f"Insufficient server fund")
                        else:
                            to_send = {
                                'id': data['id'],
                                'withdrawal_id': data['withdrawal_id'],
                                'user_id': data['user_id'],
                                'success': False,
                                'reason': status[0]
                            }
                            print(print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {status[0]}'))
                        response = requests.post(f'{web_url}/withdraw_update', json=to_send)
                        
                else: # Some error while getting withdrawal status
                    print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {status[0]}')
            await sleep(30)
        else:
            send_public_key()
            await sleep(10)






async def main():
    await asyncio.gather(monetag(), catbox(), payout())

if __name__ == "__main__":
    asyncio.run(main())