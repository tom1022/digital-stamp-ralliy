# blueprints/main/__init__.py
from flask import Blueprint

# ブループリントインスタンスを作成
# main_bpという名前で、このパッケージをルートディレクトリとします
main_bp = Blueprint('main_bp', __name__, template_folder='templates')

# routes.pyをインポートして、このブループリントにルーティングを登録
from . import routes
