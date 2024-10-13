from dotenv import load_dotenv # type: ignore
import os

load_dotenv()  # Load variables from .env
monetag_user = os.getenv("monetag_user")
monetag_pass = os.getenv("monetag_pass")
secret_key = os.getenv("FLASK_SECRET_KEY")
sql_uri = os.getenv("SQL_URI") # eg.: 'mysql+mysqldb://root:pass@localhost/flaskapp'
print(sql_uri)