from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# アプリケーションインスタンスの作成
# instance_relative_config=True は、instance/ ディレクトリから設定ファイルをロードすることを意味します
app = Flask(__name__, instance_relative_config=True)

# アプリケーション設定の読み込み
# config.py にデータベースURIや秘密鍵などを記述します
app.config.from_pyfile('config.py')

# データベース (SQLAlchemy) とログイン管理 (Flask-Login) を初期化
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_bp.login'  # ログインが必要なページのURLを指定

# ブループリントをインポート
# blueprints/main と blueprints/admin からそれぞれブループリントをインポートします
from blueprints.main.routes import main_bp
from blueprints.admin.routes import admin_bp

# ブループリントをアプリケーションに登録
# url_prefix を指定することで、admin ブループリントの全ルートに /admin というプレフィックスが付きます
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

# ユーザーローダー関数の定義
# Flask-Loginが、セッションに保存されたユーザーIDからユーザーオブジェクトをロードするために使用します
from models.users import User

@login_manager.user_loader
def load_user(user_id):
    # SQLAlchemyを使ってユーザーIDからユーザーを検索
    return db.session.get(User, int(user_id))

# アプリケーションの実行
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        from models.users import AdminUser

        # 初回起動時に管理者ユーザーを作成
        if not AdminUser.query.filter_by(username='admin').first():
            admin_user = AdminUser(username='admin')
            import string, secrets
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(8))
            admin_user.set_password()
            print(f'Your password has been set as "{password}"')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")

    app.run(debug=True)
