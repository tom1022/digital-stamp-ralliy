from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

# スタンプラリーのユーザーモデル
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    
    # 獲得したスタンプのIDをJSON形式で保存
    _stamps_collected = db.Column('stamps_collected', db.Text, default='[]')
    
    collected_stamps = db.Column(db.Integer, default=0) # 獲得スタンプ数のカウンター
    has_prize = db.Column(db.Boolean, default=False) # 景品付与フラグ

    @property
    def stamps_collected(self):
        """データベースから取得したJSON文字列をリストに変換して返す"""
        return json.loads(self._stamps_collected)

    @stamps_collected.setter
    def stamps_collected(self, value):
        """リストをJSON文字列に変換してデータベースに保存する"""
        self._stamps_collected = json.dumps(value)

# 管理者ユーザーモデル
# Flask-Loginと連携するため、UserMixinを継承
class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        """パスワードをハッシュ化して保存する"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """保存されたハッシュと入力されたパスワードを比較する"""
        return check_password_hash(self.password_hash, password)
