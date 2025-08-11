from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies
from werkzeug.security import check_password_hash
from extensions import db
from models.user import User, AdminUser
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__)

# --- APIエンドポイント ---

@admin_bp.route('/login', methods=['POST'])
def login():
    """
    管理者ログインAPI。
    JSON形式でユーザー名とパスワードを受け取り、JWTトークンを返します。
    """
    username = request.json.get('username')
    password = request.json.get('password')
    
    admin = AdminUser.query.filter_by(username=username).first()
    
    if admin and check_password_hash(admin.password_hash, password):
        access_token = create_access_token(identity=admin.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Login failed"}), 401


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """
    管理ダッシュボード用のAPI。
    ユーザー統計などの情報をJSONで返します。
    """
    total_users = User.query.count()
    completed_users = User.query.filter(User.collected_stamps >= 5).count()

    return jsonify({
        "total_users": total_users,
        "completed_users": completed_users,
        "completion_rate": f"{(completed_users / total_users * 100):.2f}%" if total_users > 0 else "0.00%",
    })


@admin_bp.route('/prize', methods=['POST'])
@jwt_required()
def register_prize():
    """
    景品付与を登録するAPI。
    ユーザーのUUIDを受け取り、景品付与日時を記録します。
    """
    user_uuid = request.json.get('uuid')
    
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if user:
        user.has_prize = True
        user.prize_awarded_at = datetime.now()
        db.session.commit()
        return jsonify({'status': 'prize_registered', 'uuid': user_uuid}), 200
    
    return jsonify({'status': 'user_not_found'}), 404


@admin_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    ログアウトAPI。
    サーバーサイドではJWTトークンを無効化します。
    """
    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response
