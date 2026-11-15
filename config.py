import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # MySQL configuration with environment defaults
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'jobportal')

    # URL-encode password to handle special symbols (e.g. '@', '#', '%')
    _encoded_pwd = urllib.parse.quote_plus(MYSQL_PASSWORD)
    DEFAULT_MYSQL_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{_encoded_pwd}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or DEFAULT_MYSQL_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
