#! usr/bin/python3.6
import os
import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/www/roll/roller')
from roller import app as application
from dotenv import load_dotenv, find_dotenv
here=os.path.dirname(__file__)
load_dotenv(f"{here}/.env")
application.secret_key = os.getenv("BW_SECRET_KEY")
print(os.getenv("BW_DATA_FOLDER"))
