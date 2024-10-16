from dotenv import load_dotenv # type: ignore
import os

# First user must be admin (id = 1)

load_dotenv()  # Load variables from .env
monetag_user = os.getenv("monetag_gmail")
monetag_pass = os.getenv("monetag_pass")
secret_key = os.getenv("flask_key")
sql_uri = os.getenv("sql_uri") # eg.: 'mysql+mysqldb://root:pass@localhost/flaskapp'
self_ad = 5 # Percentage of ad views for me