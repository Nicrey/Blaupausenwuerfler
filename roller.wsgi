import os
from roller import app as application
from dotenv import load_dotenv
load_dotenv()
application.secret_key = os.getenv("BW_SECRET_KEY")