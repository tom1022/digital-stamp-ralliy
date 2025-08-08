import os
from flask import Flask, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)

# YOLOv8のモデルをロード
model = YOLO('yolov10x.pt')  # ここでは例としてyolov8n.ptを使用

@app.route('/')
def index():
    return "YOLO and Flask are running!"

if __name__ == '__main__':
    # コンテナ内で外部からアクセスできるようにhost='0.0.0.0'を設定
    app.run(host='0.0.0.0', port=5000, debug=True)
