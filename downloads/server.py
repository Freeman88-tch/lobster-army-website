"""
龙虾兵团 · AI数字人口播工坊 Windows完整版
在电脑上运行，浏览器访问 http://localhost:5000
支持：上传照片 → AI识别 → 口播视频生成 → 预览 → 下载
"""

import os
import io
import base64
import json
import uuid
import subprocess
import tempfile
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import requests

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# ========== 前端页面 ==========
INDEX_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI数字人口播工坊 · 龙虾兵团</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a1a;color:#e2e8f0;padding:0 15px 30px}
.header{text-align:center;padding:30px 15px 15px}
.header h1{font-size:1.3em;color:#00d4ff}
.header p{color:#718096;font-size:0.8em;margin-top:4px}
.card{background:#1a1a2e;border-radius:12px;padding:18px;margin:12px 0;border:1px solid #2d2d44}
.card h3{color:#00d4ff;font-size:0.95em;margin-bottom:10px}
.upload-area{width:100%;max-width:300px;aspect-ratio:3/4;background:#2d2d44;border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;overflow:hidden;margin:0 auto 10px;position:relative}
.upload-area img{width:100%;height:100%;object-fit:cover}
.upload-area .empty{text-align:center;color:#718096;font-size:0.85em}
.upload-area .empty .icon{font-size:2.5em;margin-bottom:6px}
.btn-row{display:flex;gap:8px;justify-content:center}
.btn-row button{flex:1;max-width:160px;padding:11px;border:none;border-radius:8px;font-size:0.85em;font-weight:600;cursor:pointer}
.btn-photo{background:#2d2d44;color:#e2e8f0}
.btn-camera{background:#00d4ff22;color:#00d4ff;border:1px solid #00d4ff44}
textarea{width:100%;padding:12px;background:#2d2d44;border:1px solid #3d3d55;border-radius:8px;color:#e2e8f0;font-size:0.9em;outline:none;resize:none;min-height:80px;font-family:inherit}
textarea:focus{border-color:#00d4ff}
.voice-row{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.voice-row button{padding:8px 14px;background:#2d2d44;border:2px solid transparent;border-radius:8px;color:#a0aec0;font-size:0.8em;cursor:pointer}
.voice-row button.on{border-color:#00d4ff;background:#00d4ff11;color:#e2e8f0}
#genBtn{width:100%;padding:14px;border:none;border-radius:10px;font-size:1em;font-weight:700;cursor:pointer;margin-top:8px;transition:all .3s}
#genBtn.ok{background:linear-gradient(135deg,#00d4ff,#0099cc);color:#fff}
#genBtn.no{background:#2d2d44;color:#555;cursor:not-allowed}
#genBtn.busy{background:#48bb78;color:#fff}
#status{text-align:center;color:#718096;font-size:0.8em;padding:5px;min-height:20px}
#result{display:none;margin-top:10px;text-align:center}
#result video{width:100%;max-width:400px;border-radius:10px;border:2px solid #48bb7844}
#result .btn-down{display:inline-block;padding:12px 30px;background:#48bb78;color:#fff;border:none;border-radius:8px;font-size:1em;font-weight:700;cursor:pointer;text-decoration:none;margin-top:8px}
.footer{text-align:center;padding:20px;color:#4a5568;font-size:0.75em;margin-top:30px}
.analysis-box{background:#1a2332;border-radius:8px;padding:12px;margin:8px 0;font-size:0.85em;color:#a0aec0;line-height:1.5;white-space:pre-wrap;display:none}
</style>
</head>
<body>
<div class="header">
<h1>🎬 AI数字人口播工坊</h1>
<p>拍一张照片 → 自动生成口播视频</p>
</div>

<div class="card">
<h3>📸 上传照片</h3>
<div class="upload-area" id="uploadArea">
<div id="emptyState" class="empty"><div class="icon">📷</div><p>点击选择照片</p></div>
<img id="preview" style="display:none">
</div>
<div class="btn-row">
<button class="btn-photo" id="btnAlbum">📁 选照片</button>
<button class="btn-camera" id="btnCamera">📸 拍照</button>
</div>
</div>

<div class="card">
<h3>✍️ 口播文案</h3>
<textarea id="scriptText" placeholder="输入想让数字人说的话...">大家好，欢迎关注龙虾兵团！我们提供AI自动化解决方案，助力企业和个人降本增效。如果你也想用AI提升效率，欢迎联系我们！</textarea>
<h3 style="margin-top:14px">🎤 配音</h3>
<div class="voice-row">
<button class="on">👩 晓伊</button><button>🧑 云健</button>
<button>👩 婉秋</button><button>🧑 志刚</button>
</div>
</div>

<div class="card">
<h3>🚀 AI分析 + 生成视频</h3>
<button id="genBtn" class="no">📷 请先上传照片</button>
<div id="status"></div>
<div class="analysis-box" id="analysisBox"></div>
<div id="result"></div>
</div>

<div class="footer">🦞 龙虾兵团 · AI自动化工具箱</div>

<input type="file" id="fileInput" accept="image/*" style="display:none">
<input type="file" id="cameraInput" accept="image/*" capture="environment" style="display:none">

<script>
var photoData = null;
document.getElementById('btnAlbum').onclick = function(){document.getElementById('fileInput').click()};
document.getElementById('btnCamera').onclick = function(){document.getElementById('cameraInput').click()};
document.getElementById('uploadArea').onclick = function(){document.getElementById('fileInput').click()};

document.getElementById('fileInput').onchange = function(){loadPhoto(this)};
document.getElementById('cameraInput').onchange = function(){loadPhoto(this)};

function loadPhoto(inp){
  var f=inp.files[0];if(!f)return;
  var r=new FileReader();
  r.onload=function(e){
    photoData=e.target.result;
    document.getElementById('preview').src=photoData;
    document.getElementById('preview').style.display='block';
    document.getElementById('emptyState').style.display='none';
    checkReady();
  };
  r.readAsDataURL(f);
}

document.querySelectorAll('.voice-row button').forEach(function(b){
  b.onclick=function(){
    document.querySelectorAll('.voice-row button').forEach(function(x){x.className=''});
    this.className='on';
  }
});

document.getElementById('scriptText').oninput=checkReady;

function checkReady(){
  var btn=document.getElementById('genBtn');
  var s=document.getElementById('scriptText').value.trim();
  if(photoData&&s){btn.className='btn ok';btn.textContent='🚀 AI分析 + 生成口播视频'}
  else if(!photoData){btn.className='btn no';btn.textContent='📷 请先上传照片'}
  else{btn.className='btn no';btn.textContent='✍️ 请填写文案'}
}

function getVoice(){
  var btns=document.querySelectorAll('.voice-row button');
  for(var i=0;i<btns.length;i++)if(btns[i].className=='on')return btns[i].textContent.trim();
  return '晓伊';
}

function generate(){
  var btn=document.getElementById('genBtn');
  if(btn.className.indexOf('ok')===-1)return;
  var status=document.getElementById('status');
  var analysisBox=document.getElementById('analysisBox');
  var result=document.getElementById('result');
  result.style.display='none';
  analysisBox.style.display='none';
  
  // 第一步：AI分析照片
  status.textContent='🔍 AI正在分析照片...';
  btn.className='btn busy';btn.textContent='🔍 分析中...';
  
  var xhr=new XMLHttpRequest();
  xhr.open('POST','/api/analyze-photo',true);
  xhr.setRequestHeader('Content-Type','application/json');
  xhr.onload=function(){
    try{
      var d=JSON.parse(xhr.responseText);
      if(d.success){
        analysisBox.textContent=d.analysis;
        analysisBox.style.display='block';
        
        if(d.video_url){
          // 有视频了
          status.textContent='✅ 视频生成完成！';
          btn.className='btn ok';btn.textContent='✅ 已完成';
          result.innerHTML='<video src="'+d.video_url+'" controls autoplay></video><br><a class="btn-down" href="'+d.video_url+'" download>⬇ 下载视频</a>';
          result.style.display='block';
        }else{
          // 只有分析结果，继续生成
          doGenerate(d);
        }
      }else{
        status.textContent='⚠️ 分析失败';btn.className='btn ok';btn.textContent='🔄 重试';
      }
    }catch(e){
      status.textContent='⚠️ 请求失败: '+e.message;btn.className='btn ok';btn.textContent='🔄 重试';
    }
  };
  xhr.onerror=function(){status.textContent='⚠️ 无法连接后端';btn.className='btn ok';btn.textContent='🔄 重试'};
  xhr.send(JSON.stringify({photo:photoData,script:document.getElementById('scriptText').value.trim(),voice:getVoice()}));
}

// 用实际图片生成视频
function doGenerate(data){
  var status=document.getElementById('status');
  var btn=document.getElementById('genBtn');
  var analysisBox=document.getElementById('analysisBox');
  
  status.textContent='🎬 正在生成口播视频...';
  btn.textContent='🎬 渲染中...';
  
  // 后端生成视频
  var xhr2=new XMLHttpRequest();
  xhr2.open('POST','/api/generate-video',true);
  xhr2.setRequestHeader('Content-Type','application/json');
  xhr2.onload=function(){
    try{
      var d2=JSON.parse(xhr2.responseText);
      if(d2.success&&d2.video_url){
        status.textContent='✅ 视频生成完成！';
        btn.className='btn ok';btn.textContent='✅ 已完成';
        var result=document.getElementById('result');
        result.innerHTML='<video src="'+d2.video_url+'" controls autoplay></video><br><a class="btn-down" href="'+d2.video_url+'" download>⬇ 下载视频</a>';
        result.style.display='block';
        analysisBox.style.display='none';
      }else{
        status.textContent='⚠️ 生成失败';btn.className='btn ok';btn.textContent='🔄 重试';
      }
    }catch(e){
      status.textContent='⚠️ 错误: '+e.message;btn.className='btn ok';btn.textContent='🔄 重试';
    }
  };
  xhr2.onerror=function(){
    // 后端无模型时，用静态图片+文字生成演示视频
    createDemoVideo(data.photo);
  };
  xhr2.send(JSON.stringify({photo:photoData,script:document.getElementById('scriptText').value.trim(),voice:getVoice()}));
}

function createDemoVideo(photo){
  var status=document.getElementById('status');
  var btn=document.getElementById('genBtn');
  var analysisBox=document.getElementById('analysisBox');
  
  status.textContent='🎬 生成演示视频...';
  
  var xhr=new XMLHttpRequest();
  xhr.open('POST','/api/create-demo',true);
  xhr.setRequestHeader('Content-Type','application/json');
  xhr.onload=function(){
    try{
      var d=JSON.parse(xhr.responseText);
      if(d.success&&d.video_url){
        status.textContent='✅ 视频生成完成！';
        btn.className='btn ok';btn.textContent='✅ 已完成';
        var result=document.getElementById('result');
        result.innerHTML='<video src="'+d.video_url+'" controls autoplay></video><br><a class="btn-down" href="'+d.video_url+'" download>⬇ 下载视频</a>';
        result.style.display='block';
        analysisBox.style.display='none';
        return;
      }
    }catch(e){}
    status.textContent='⚠️ 生成失败，请确认后端已安装完整模型';btn.className='btn ok';btn.textContent='🔄 重试';
  };
  xhr.send(JSON.stringify({photo:photo}));
}

document.getElementById('genBtn').onclick=generate;
</script>
</body></html>"""

@app.route("/")
def index():
    return INDEX_HTML

# ========== API: 照片分析 ==========
@app.route("/api/analyze-photo", methods=["POST", "OPTIONS"])
def analyze_photo():
    if request.method == "OPTIONS":
        return "", 200
    
    data = request.json
    photo_b64 = data.get("photo", "")
    script = data.get("script", "")
    voice = data.get("voice", "")
    
    if not photo_b64:
        return jsonify({"success": False, "error": "no photo"})
    
    task_id = str(uuid.uuid4())[:8]
    
    try:
        # 保存照片
        image_data = base64.b64decode(photo_b64.split(",")[1])
        img_path = os.path.join(OUTPUT_DIR, f"{task_id}_input.jpg")
        with open(img_path, "wb") as f:
            f.write(image_data)
        
        # 调豆包API识别照片
        analysis = call_doubao_vision(image_data)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "script": script,
            "voice": voice,
            "task_id": task_id,
            "photo_path": img_path
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ========== 豆包API视觉识别 ==========
DOUBAO_KEY = "ark-a9fabe47-c00b-46e7-909a-0fd9b2b47777-8f0e0"
DOUBAO_MODEL = "ep-20260509014909-lvs7s"
DOUBAO_API = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

def call_doubao_vision(image_data):
    """调豆包视觉API分析照片特征"""
    import base64
    b64 = base64.b64encode(image_data).decode()
    
    payload = {
        "model": DOUBAO_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "请分析这张照片中的人物特征，用中文简明回答（3-5句话）：\n1. 性别和大致年龄\n2. 面部朝向\n3. 表情状态\n4. 光线条件\n5. 是否适合做数字人口播？建议理由是什么？"
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                }
            ]
        }],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    try:
        resp = requests.post(
            DOUBAO_API,
            headers={
                "Authorization": f"Bearer {DOUBAO_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get("message", "未知错误")
            return f"⚠️ 豆包API调用失败: {error_msg}"
    except Exception as e:
        return f"⚠️ API请求失败: {str(e)}"

# ========== API: 生成口播视频（使用实际照片+配音） ==========
@app.route("/api/generate-video", methods=["POST", "OPTIONS"])
def generate_video():
    if request.method == "OPTIONS":
        return "", 200
    
    data = request.json
    photo_b64 = data.get("photo", "")
    script = data.get("script", "大家好")
    voice = data.get("voice", "晓伊")
    
    task_id = str(uuid.uuid4())[:8]
    
    # 保存照片
    image_data = base64.b64decode(photo_b64.split(",")[1])
    img_path = os.path.join(OUTPUT_DIR, f"{task_id}_input.jpg")
    with open(img_path, "wb") as f:
        f.write(image_data)
    
    # 用FFmpeg生成动态视频（照片+配音文字）
    video_path = os.path.join(OUTPUT_DIR, f"{task_id}_output.mp4")
    audio_path = os.path.join(OUTPUT_DIR, f"{task_id}_audio.mp4")
    
    try:
        # 尝试用gTTS生成中文配音
        try:
            from gtts import gTTS
            tts_audio = os.path.join(OUTPUT_DIR, f"{task_id}_tts.mp3")
            tts = gTTS(text=script, lang="zh-CN", slow=False)
            tts.save(tts_audio)
            audio_source = tts_audio
        except:
            # 没有gTTS，用静音音频替代
            audio_source = None
        
        # 用FFmpeg生成视频: 照片+配音
        if audio_source:
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", img_path,
                "-i", audio_source,
                "-c:v", "libx264",
                "-t", str(max(5, len(script) // 4)),
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        else:
            # 无音频，生成带文字的视频
            # 先用PIL在照片上加文字
            from PIL import ImageDraw, ImageFont
            img = Image.open(img_path).convert("RGB")
            img = img.resize((1080, 1920), Image.LANCZOS)
            draw = ImageDraw.Draw(img)
            
            # 尝试加中文字体
            font = None
            for fp in [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/msyh.ttf",
            ]:
                if os.path.exists(fp):
                    try:
                        font = ImageFont.truetype(fp, 48)
                        break
                    except:
                        pass
            
            if font:
                # 在图片底部加文字区域
                lines = []
                line = ""
                for word in script:
                    line += word
                    if len(line) >= 15 or word in "。！？，":
                        lines.append(line)
                        line = ""
                if line:
                    lines.append(line)
                
                y = 1500
                for l in lines[:6]:
                    bbox = draw.textbbox((0, 0), l, font=font)
                    tw = bbox[2] - bbox[0]
                    draw.text(((1080 - tw) // 2, y), l, fill="white", font=font)
                    y += 60
            
            text_img_path = os.path.join(OUTPUT_DIR, f"{task_id}_text.jpg")
            img.save(text_img_path, quality=95)
            
            # 生成简单视频
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", text_img_path,
                "-c:v", "libx264",
                "-t", "8",
                "-pix_fmt", "yuv420p",
                "-vf", "fps=24",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if os.path.exists(video_path):
            video_url = f"/output/{task_id}_output.mp4"
            return jsonify({"success": True, "video_url": video_url, "task_id": task_id})
        else:
            return jsonify({"success": False, "error": "FFmpeg output not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ========== API: 创建演示视频（纯图片转视频） ==========
@app.route("/api/create-demo", methods=["POST", "OPTIONS"])
def create_demo():
    if request.method == "OPTIONS":
        return "", 200
    
    data = request.json
    photo_b64 = data.get("photo", "")
    
    task_id = str(uuid.uuid4())[:8]
    image_data = base64.b64decode(photo_b64.split(",")[1])
    img_path = os.path.join(OUTPUT_DIR, f"{task_id}_demo.jpg")
    with open(img_path, "wb") as f:
        f.write(image_data)
    
    video_path = os.path.join(OUTPUT_DIR, f"{task_id}_demo.mp4")
    
    try:
        # 用FFmpeg将图片转成5秒视频
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-c:v", "libx264",
            "-t", "5",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            video_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if os.path.exists(video_path):
            video_url = f"/output/{task_id}_demo.mp4"
            return jsonify({"success": True, "video_url": video_url})
    except:
        pass
    
    return jsonify({"success": False})

# ========== 静态文件路由 ==========
@app.route("/output/<filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    print("🦞 龙虾兵团 · AI数字人口播工坊")
    print("=" * 40)
    print("服务地址: http://localhost:5000")
    print("手机访问: http://你的IP:5000")
    print()
    print("打开浏览器即可使用：")
    print("  1. 上传照片")
    print("  2. 写文案")
    print("  3. 选配音")
    print("  4. 点生成 → 预览 → 下载")
    print("=" * 40)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
