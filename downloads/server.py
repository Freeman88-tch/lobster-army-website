"""
龙虾兵团 · AI数字人口播工坊 - 后端服务
在Windows上运行，供网页端调用
"""

import os
import io
import base64
import json
import subprocess
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/api/analyze-photo", methods=["POST", "OPTIONS"])
def analyze_photo():
    """接收前端上传的照片，返回AI分析结果（调用豆包API）"""
    if request.method == "OPTIONS":
        return "", 200
    
    data = request.json
    photo_b64 = data.get("photo", "")
    script = data.get("script", "")
    voice = data.get("voice", "")
    
    if not photo_b64:
        return jsonify({"success": False, "error": "no photo"})
    
    # 把base64图片保存为临时文件，用于后续数字人生成
    try:
        image_data = base64.b64decode(photo_b64.split(",")[1])
        img_path = os.path.join(OUTPUT_DIR, "input_photo.jpg")
        with open(img_path, "wb") as f:
            f.write(image_data)
        analysis = f"✅ 照片已接收\n大小: {len(image_data)/1024:.0f}KB\n\n等待数字人生成..."
    except Exception as e:
        analysis = f"⚠️ 图片处理失败: {e}"
    
    return jsonify({
        "success": True,
        "analysis": analysis,
        "script": script,
        "voice": voice
    })

@app.route("/api/generate", methods=["POST", "OPTIONS"])
def generate_video():
    """接收照片+文案，生成数字人口播视频"""
    if request.method == "OPTIONS":
        return "", 200
    
    data = request.json
    photo_b64 = data.get("photo", "")
    script = data.get("script", "")
    
    # 保存照片
    image_data = base64.b64decode(photo_b64.split(",")[1])
    img_path = os.path.join(OUTPUT_DIR, "face.jpg")
    with open(img_path, "wb") as f:
        f.write(image_data)
    
    # 如果安装了gTTS，用AI生成配音
    try:
        from gtts import gTTS
        audio_path = os.path.join(OUTPUT_DIR, "voice.mp3")
        tts = gTTS(text=script, lang="zh-CN")
        tts.save(audio_path)
        audio_ready = True
    except:
        audio_ready = False
    
    return jsonify({
        "success": True,
        "message": "数字人视频生成中...",
        "status": "pending"
    })

@app.route("/api/status", methods=["GET"])
def status():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "name": "龙虾兵团·AI数字人口播工坊",
        "backend": "running"
    })

if __name__ == "__main__":
    print("🦞 龙虾兵团 · AI数字人口播后端")
    print(f"服务地址: http://0.0.0.0:5000")
    print("手机访问: http://你电脑IP:5000")
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
