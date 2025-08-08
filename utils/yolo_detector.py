import torch
import json
import os
from ultralytics import YOLO

# このスクリプトのディレクトリを取得
# 相対パスを解決するために使用
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. YOLOv10モデルのロード
# アプリケーション起動時に一度だけモデルをロードすることで、推論のパフォーマンスを向上させます。
MODEL_PATH = os.path.join(current_dir, '..', 'data', 'yolov10x.pt')
try:
    # GPU (CUDA) が利用可能であれば使用し、そうでなければCPUを使用
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # YOLOモデルのインスタンスを作成し、指定されたデバイスにロード
    model = YOLO(MODEL_PATH)
    model.to(device)
    print(f"YOLOv10 model loaded on {device}.")
except Exception as e:
    print(f"Failed to load YOLO model: {e}")
    model = None

# 2. チェックポイント（ランドマーク）情報のロード
# 認識されたYOLOのクラスIDと、スタンプラリーのスタンプIDの対応関係を定義
CHECKPOINTS_PATH = os.path.join(current_dir, '..', 'data', 'landmarks.json')
try:
    with open(CHECKPOINTS_PATH, 'r', encoding='utf-8') as f:
        checkpoints_data = json.load(f)
    print("Checkpoints data loaded.")
except FileNotFoundError:
    print(f"Checkpoints file not found at {CHECKPOINTS_PATH}.")
    checkpoints_data = {}

def detect_landmark(image_path: str):
    """
    指定された画像パスのファイルからランドマークを検出し、
    対応するスタンプIDを返す関数。
    
    Args:
        image_path (str): 認識する画像のファイルパス。
        
    Returns:
        str or None: 検出されたランドマークのスタンプID。見つからない場合はNone。
    """
    if model is None:
        print("Model is not loaded. Cannot perform detection.")
        return None

    try:
        # 3. モデルを使って推論を実行
        # conf（信頼度閾値）とiou（重複除去閾値）を設定
        results = model.predict(image_path, conf=0.5, iou=0.7)
        
        # 4. 推論結果の解析
        best_result_cls = None
        best_conf = 0.5  # 信頼度閾値より高い結果のみを考慮
        
        for result in results:
            for box in result.boxes:
                conf = box.conf.item()  # 信頼度
                cls = int(box.cls.item())  # クラスID
                
                # 信頼度が最も高い検出結果を更新
                if conf > best_conf:
                    best_conf = conf
                    best_result_cls = cls

        # 5. チェックポイントデータと照合
        if best_result_cls is not None:
            # `checkpoints_data`はキーが文字列のクラスIDを想定
            yolo_class_id = str(best_result_cls)
            
            if yolo_class_id in checkpoints_data:
                print(f"Detected landmark with class_id {yolo_class_id}.")
                return checkpoints_data[yolo_class_id]
        
        print("No valid landmark detected.")
        return None
        
    except Exception as e:
        print(f"Error during detection: {e}")
        return None
