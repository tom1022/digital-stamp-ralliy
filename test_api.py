import requests
import json
import os
import time
from unittest.mock import patch

# Flaskアプリケーションが実行されているベースURL
BASE_URL = "http://127.0.0.1:5000"

# テスト用の管理者認証情報
ADMIN_USERNAME = "test_admin"
ADMIN_PASSWORD = "test_password"

# ファイルパスの定義
TEST_DUMMY_IMAGE_PATH = "test_dummy_image.jpg"
TEST_VALID_IMAGE_PATH = "test_valid_image.jpg"
LANDMARKS_PATH = os.path.join(os.path.dirname(__file__), 'data/landmarks.json')

def run_tests():
    print("--- Running API Tests ---")
    
    test_user_uuid = None
    access_token = None
    
    landmarks_file_exists = os.path.exists(LANDMARKS_PATH)
    if not landmarks_file_exists:
        print(f"Creating temporary {LANDMARKS_PATH} for testing...")
        os.makedirs(os.path.dirname(LANDMARKS_PATH), exist_ok=True)
        with open(LANDMARKS_PATH, 'w') as f:
            # テスト用に5つのスタンプを定義
            json.dump({"0": "faculty of information", "1": "library", "2": "maingate"}, f)

    # テスト用のダミー画像ファイルを作成
    with open(TEST_DUMMY_IMAGE_PATH, "w") as f:
        f.write("dummy image data")

    try:
        # --- テスト用のランドマーク情報をロード ---
        with open(LANDMARKS_PATH, 'r', encoding='utf-8') as f:
            test_landmarks = json.load(f)
        stamp_ids = list(test_landmarks.values())

        # --- 1. ユーザーAPIのテスト ---
        print("\n--- Testing User API (/main) ---")

        # 1.1 新規ユーザー作成テスト
        print("Test 1.1: Create new user...")
        response = requests.post(f"{BASE_URL}/", headers={'Content-Type': 'application/json'})
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'new_user'
        test_user_uuid = data['user_uuid']
        print(f"✅ Success: New user created with UUID: {test_user_uuid}")
        
        user_headers = {'X-User-UUID': test_user_uuid}

        # 1.2 既存ユーザー取得テスト
        print("Test 1.2: Get existing user info...")
        response = requests.post(f"{BASE_URL}/", headers=user_headers)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'existing_user'
        assert data['user_uuid'] == test_user_uuid
        print("✅ Success: Existing user info retrieved.")

        # 1.3 画像アップロードテスト (失敗パターン: ダミー画像)
        print("Test 1.3: Upload dummy image and expect no stamp...")
        with patch('utils.yolo_detector.detect_landmark', return_value=None):
            with open(TEST_DUMMY_IMAGE_PATH, 'rb') as f:
                files = {'file': (os.path.basename(TEST_DUMMY_IMAGE_PATH), f, 'image/jpeg')}
                response = requests.post(f"{BASE_URL}/upload", headers=user_headers, files=files)
                print(f"Response: {response.json()}")
                assert response.status_code == 200
                data = response.json()
                assert data['status'] == 'no_new_stamp'
                print("✅ Success: No stamp granted for dummy image.")

        # 1.4 画像アップロードテスト (成功パターン: 複数スタンプ獲得)
        # print("Test 1.4: Upload valid images and grant stamps until completion...")
        
        # for i, stamp_id in enumerate(stamp_ids):
        #     # utils.yolo_detectorモジュールのdetect_landmark関数をモック化
        #     with patch('utils.yolo_detector.detect_landmark', return_value=stamp_id):
        #         with open(TEST_DUMMY_IMAGE_PATH, 'rb') as f: # ダミー画像を使ってモックで成功をシミュレート
        #             files = {'file': (os.path.basename(TEST_VALID_IMAGE_PATH), f, 'image/jpeg')}
        #             response = requests.post(f"{BASE_URL}/upload", headers=user_headers, files=files)
        #             print(f"Response: {response.json()}")
        #             assert response.status_code == 200
        #             data = response.json()
        #             assert data['status'] == 'stamp_granted'
        #             assert data['landmark_id'] == stamp_id
        #             print(f"✅ Success: Stamp {i+1} granted: {data['landmark_id']}")

        # 1.5 全スタンプ獲得後のfinalページテスト
        # print("Test 1.5: Check final page after completing all stamps...")
        # response = requests.get(f"{BASE_URL}/final", headers=user_headers)
        # print(f"Response: {response.json()}")
        # assert response.status_code == 200
        # data = response.json()
        # assert data['status'] == 'complete'
        # assert data['user_uuid'] == test_user_uuid
        # print("✅ Success: Final page shows completion.")

        # --- 2. 管理者APIのテスト ---
        print("\n--- Testing Admin API (/admin) ---")

        # 2.1 ログインテスト (失敗)
        print("Test 2.1: Admin login with bad credentials...")
        login_data = {'username': ADMIN_USERNAME, 'password': 'wrong_password'}
        response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
        print(f"Response: {response.json()}")
        assert response.status_code == 401
        print("✅ Success: Login failed with wrong password.")

        # 2.2 ログインテスト (成功)
        print("Test 2.2: Admin login with correct credentials...")
        login_data = {'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        access_token = response.json()['access_token']
        admin_headers = {'Authorization': f'Bearer {access_token}'}
        print("✅ Success: JWT access token received.")

        # 2.3 ダッシュボードテスト
        print("Test 2.3: Get admin dashboard data...")
        response = requests.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert 'total_users' in data
        assert 'completed_users' in data
        print("✅ Success: Admin dashboard data retrieved.")

        # 2.4 ユーザー一覧テスト
        print("Test 2.4: Get users list...")
        response = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert 'users' in data
        assert 'total_users' in data
        print("✅ Success: Users list retrieved.")

        # 2.5 景品付与テスト
        print("Test 2.5: Award prize to user...")
        prize_data = {'uuid': test_user_uuid}
        response = requests.post(f"{BASE_URL}/admin/prize", headers=admin_headers, json=prize_data)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'prize_registered'
        print("✅ Success: Prize awarded to user.")
        
        # 2.6 ログアウトテスト
        print("Test 2.6: Admin logout...")
        response = requests.post(f"{BASE_URL}/admin/logout", headers=admin_headers)
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✅ Success: Logged out.")

        print("\n--- All tests passed! ---")

    finally:
        # クリーンアップ処理
        print("\n--- Cleaning up ---")
        if os.path.exists(TEST_DUMMY_IMAGE_PATH):
            os.remove(TEST_DUMMY_IMAGE_PATH)
        if not landmarks_file_exists and os.path.exists(LANDMARKS_PATH):
            os.remove(LANDMARKS_PATH)
        print("Cleanup complete.")

if __name__ == "__main__":
    run_tests()
