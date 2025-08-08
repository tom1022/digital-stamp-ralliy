# blueprints/admin/__init__.py
from flask import Blueprint

# ブループリントインスタンスを作成
# admin_bpという名前で、このパッケージをルートディレクトリとします
admin_bp = Blueprint('admin_bp', __name__, template_folder='templates')

# routes.pyをインポートして、このブループリントにルーティングを登録
from . import routes
