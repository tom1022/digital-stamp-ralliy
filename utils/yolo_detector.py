import json
import os
from ultralytics import YOLO
from torch import cuda

current_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(current_dir, '..', 'data', 'best.pt')
try:
    device = 'cuda' if cuda.is_available() else 'cpu'
    
    model = YOLO(MODEL_PATH)
    model.to(device)
    print(f"YOLOv10 model loaded on {device}.")
except Exception as e:
    print(f"Failed to load YOLO model: {e}")
    model = None

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
        results = model.predict(image_path, conf=0.5, iou=0.7)
        
        best_result_cls = None
        best_conf = 0.5 
        
        for result in results:
            for box in result.boxes:
                conf = box.conf.item() 
                cls = int(box.cls.item()) 
                
                if conf > best_conf:
                    best_conf = conf
                    best_result_cls = cls

        if best_result_cls is not None:
            yolo_class_id = str(best_result_cls)

            print(f"cls: {cls}, conf: {conf}, yolo_class_id: {yolo_class_id}")

            if yolo_class_id in checkpoints_data:
                print(f"Detected landmark with class_id {yolo_class_id}.")
                return checkpoints_data[yolo_class_id]
        
        print("No valid landmark detected.")
        return None
        
    except Exception as e:
        print(f"Error during detection: {e}")
        return None


if __name__ == "__main__":
    image_path = "test/test_valid_image.jpg"
    landmark_id = detect_landmark(image_path)
    print(f"Detected landmark ID: {landmark_id}")
