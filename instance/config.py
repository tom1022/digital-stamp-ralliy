# instance/config.py
import secrets

SECRET_KEY = secrets.token_hex(16)
SQLALCHEMY_DATABASE_URI = 'sqlite:///stamp_rally.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = secrets.token_hex(16)
