# blueprints/main/routes.py
from flask import render_template, request, jsonify, make_response, redirect, url_for
import uuid
import os
from app import db # app.pyで定義したdbインスタンスをインポート
from models.users import User
from . import main_bp
from utils.yolo_detector import detect_landmark

# トップページ
@main_bp.route('/')
def index():
    user_uuid = request.cookies.get('uuid')
    if not user_uuid:
        # UUIDが存在しない場合、新しいUUIDを作成しクッキーに保存
        user_uuid = str(uuid.uuid4())
        new_user = User(uuid=user_uuid, collected_stamps=0, has_prize=False)
        db.session.add(new_user)
        db.session.commit()
        
        response = make_response(render_template('index.html'))
        response.set_cookie('uuid', user_uuid)
        return response

    # UUIDが存在する場合、ユーザー情報を取得して表示
    user = User.query.filter_by(uuid=user_uuid).first()
    if user and user.collected_stamps >= 5: # 例：スタンプが5つでコンプリート
        return redirect(url_for('main_bp.final_page'))

    return render_template('index.html')

# 画像アップロードページ
@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    user_uuid = request.cookies.get('uuid')
    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return redirect(url_for('main_bp.index'))

    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # 画像をサーバーに一時保存
        image_path = os.path.join('/tmp', image_file.filename)
        image_file.save(image_path)

        # YOLOv10で画像認識を実行
        landmark_id = detect_landmark(image_path)
        os.remove(image_path) # 一時ファイルを削除

        if landmark_id and landmark_id not in user.stamps_collected:
            # 新しいスタンプの場合、データベースを更新
            user.stamps_collected.append(landmark_id)
            user.collected_stamps = len(user.stamps_collected)
            db.session.commit()
            return jsonify({'status': 'stamp_granted', 'landmark_id': landmark_id})
        
        return jsonify({'status': 'no_new_stamp'})

    return render_template('upload.html')

# 全スタンプ獲得後のQRコード表示ページ
@main_bp.route('/final')
def final_page():
    user_uuid = request.cookies.get('uuid')
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if user and user.collected_stamps >= 5:
        # QRコード生成ロジックはテンプレート側でuuidを使って実行
        return render_template('final.html', user_uuid=user_uuid)
    
    return redirect(url_for('main_bp.index'))
