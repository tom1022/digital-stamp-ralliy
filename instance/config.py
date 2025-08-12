import os
import secrets

SECRET_KEY = secrets.token_hex(16)
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}@{os.environ.get('MYSQL_HOST', 'db')}:{os.environ.get('MYSQL_PORT', '3306')}/{os.environ.get('MYSQL_DATABASE')}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = secrets.token_hex(16)
