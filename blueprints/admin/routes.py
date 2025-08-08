# blueprints/admin/routes.py
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app import db
from models.users import User, AdminUser
from . import admin_bp

# ログインページ
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # データベースから管理者ユーザーを検索
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            flash('ログインに成功しました。', 'success')
            return redirect(url_for('admin_bp.admin_panel'))
        else:
            flash('ユーザー名またはパスワードが正しくありません。', 'danger')

    return render_template('admin_login.html')

# 管理者パネル
@admin_bp.route('/')
@login_required
def admin_panel():
    return render_template('admin_panel.html')

# 景品付与の登録（QRコードスキャン後）
@admin_bp.route('/prize', methods=['POST'])
@login_required
def register_prize():
    user_uuid = request.json.get('uuid')
    
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if user:
        # DBを更新して景品付与を登録
        user.has_prize = True
        db.session.commit()
        return jsonify({'status': 'prize_registered', 'user_uuid': user_uuid})
    
    return jsonify({'status': 'user_not_found'}), 404

# ログアウト
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('admin_bp.login'))
