import os
import requests
from dotenv import load_dotenv
import moltin

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MOLTIN_TOKEN = moltin.get_oauth_access_token(CLIENT_ID, CLIENT_SECRET)
