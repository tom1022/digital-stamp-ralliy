from flask import Blueprint, request, jsonify
import uuid
import os
import json
from extensions import db
from models.user import User
from utils.yolo_detector import detect_landmark

main_bp = Blueprint('main_bp', __name__)

# ランドマーク情報を読み込む関数
def load_landmarks():
    landmarks_path = os.path.join(os.path.dirname(__file__), '../../data/landmarks.json')
    try:
        with open(landmarks_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_user_from_header():
    """リクエストヘッダーからUUIDを取得し、ユーザーを返すヘルパー関数"""
    user_uuid = request.headers.get('X-User-UUID')
    if user_uuid:
        return User.query.filter_by(uuid=user_uuid).first()
    return None

# --- APIエンドポイント ---

@main_bp.route('/', methods=['POST'])
def create_or_get_user():
    """UUIDを生成または取得し、ユーザー情報を返す"""
    user = get_user_from_header()
    
    if not user:
        # 新規ユーザーの場合
        new_uuid = str(uuid.uuid4())
        new_user = User(uuid=new_uuid, collected_stamps=0, has_prize=False)
        db.session.add(new_user)
        db.session.commit()
        
        all_landmarks = load_landmarks()
        
        return jsonify({
            'status': 'new_user',
            'user_uuid': new_uuid,
            'landmarks': {
                'collected': [],
                'uncollected': [{'id': k, 'name': v} for k, v in all_landmarks.items() if k != '000']
            }
        })

    # 既存ユーザーの場合
    all_landmarks = load_landmarks()
    collected_landmark_ids = user.stamps_collected if hasattr(user, 'stamps_collected') else []
    
    landmarks = {
        'collected': [{'id': lid, 'name': all_landmarks.get(lid)} for lid in collected_landmark_ids if lid in all_landmarks],
        'uncollected': [{'id': k, 'name': v} for k, v in all_landmarks.items() if k not in collected_landmark_ids and k != '000']
    }

    return jsonify({
        'status': 'existing_user',
        'user_uuid': user.uuid,
        'landmarks': landmarks,
        'collected_stamps_count': user.collected_stamps
    })


@main_bp.route('/upload', methods=['POST'])
def upload():
    user = get_user_from_header()
    if not user:
        return jsonify({'error': 'User not found. Please provide a valid UUID header.'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    image_file = request.files['file']
    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    image_path = os.path.join('/tmp', f"{user.uuid}_{image_file.filename}")
    image_file.save(image_path)

    landmark_id = detect_landmark(image_path)
    os.remove(image_path)

    if landmark_id and landmark_id not in user.stamps_collected:
        user.stamps_collected.append(landmark_id)
        user.collected_stamps = len(user.stamps_collected)
        db.session.commit()
        return jsonify({'status': 'stamp_granted', 'landmark_id': landmark_id})
    
    return jsonify({'status': 'no_new_stamp'})

@main_bp.route('/final', methods=['GET'])
def final_page():
    user = get_user_from_header()
    if not user:
        return jsonify({'error': 'User not found. Please provide a valid UUID header.'}), 404

    # ここではコンプリートに必要なスタンプ数を5つと仮定
    if user.collected_stamps >= 5:
        return jsonify({
            'status': 'complete',
            'user_uuid': user.uuid,
            'has_prize': user.has_prize
        })

    return jsonify({'status': 'not_complete', 'message': 'The user has not collected enough stamps.'})
