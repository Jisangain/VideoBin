from time import sleep
import settings
import requests

user = settings.monetag_user
password = settings.monetag_pass
while True:
    try:
        with open('token.txt', 'r') as f:
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

            total_balance = balance_response.json().get('balance') + balance_response.json().get('hold_earning')
            print("Total balance:", total_balance)
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
            # Update the token in token.json
            with open('token.txt', 'w') as f:
                f.write(token)
            
        else:
            print("Login failed. Status Code:", login_response.status_code)
            print("Response:", login_response.json())

    else:
        sleep(10)