import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv('BASE_URL')
API_KEY = os.getenv('API_KEY')
MAIL_USERNAME = os.getenv('USERNAME')
MAIL_PASSWORD = os.getenv('PASSWORD')

# Flask-Mail config
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'tranngoctonhu2405@gmail.com'
MAIL_PASSWORD = os.getenv('PASSWORD')

# Celery config
CELERY_BROKER_URL = 'redis://localhost:6379/0'
