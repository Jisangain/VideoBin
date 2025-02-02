from dotenv import load_dotenv # type: ignore
import os

# First user must be admin (id = 1)

load_dotenv()  # Load variables from .env
monetag_user = os.getenv("monetag_gmail")
monetag_pass = os.getenv("monetag_pass")
connector_key = os.getenv("connector_key") # Make sure this is same in both flask and monetag_update.py files
secret_key = os.getenv("flask_key")
binance_api = os.getenv("binance_api")
binance_secret = os.getenv("binance_secret")
sql_uri = os.getenv("sql_uri") # eg.: 'mysql+mysqldb://root:pass@localhost/flaskapp'
web_url = os.getenv("web_url") # My website url( include http:// or https://)
self_ad = 5 # Percentage of ad views for web admin
encryption_method = 'scrypt' # Encryption method for passwords, change to 'sha256' if scrypt is not available