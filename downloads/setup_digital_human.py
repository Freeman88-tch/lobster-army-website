"""
龙虾兵团 · AI数字人口播工坊 - Windows一键安装脚本
只需要运行这个文件，自动安装所有依赖
"""

import os
import sys
import subprocess
import platform

print("=" * 50)
print("🦞 龙虾兵团 · AI数字人口播工坊")
print("=" * 50)
print(f"系统: {platform.system()} {platform.release()}")
print()

# 检查Python版本
print("[1/4] 检查Python环境...")
if sys.version_info < (3, 8):
    print("❌ Python版本过低，需要3.8+")
    print("   请下载: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe")
    sys.exit(1)
print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# 安装依赖
print()
print("[2/4] 安装Python依赖...")
deps = [
    "torch>=2.0.0",
    "torchvision>=0.15.0",
    "numpy",
    "opencv-python",
    "pillow",
    "scipy",
    "imageio",
    "imageio-ffmpeg",
    "gdown",
    "requests",
    "soundfile",
    "librosa",
    "flask",
    "flask-cors",
]

for dep in deps:
    print(f"   安装 {dep}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", dep, "-q"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"   ⚠️ {dep} 安装遇到问题，继续...")

print("✅ 依赖安装完成")

# 下载模型文件
print()
print("[3/4] 下载模型文件...")

import requests

models = {
    "wav2lip_gan.pth": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth",
    "face_parsing.pth": "https://github.com/zllrunning/face-parsing.PyTorch/releases/download/v1.0/face_parsing.pth",
}

models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(models_dir, exist_ok=True)

for name, url in models.items():
    path = os.path.join(models_dir, name)
    if os.path.exists(path):
        print(f"   ✅ {name} 已存在")
        continue
    print(f"   下载 {name}...")
    try:
        r = requests.get(url, timeout=30)
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"   ✅ {name} 下载完成 ({len(r.content)/1024/1024:.1f}MB)")
    except Exception as e:
        print(f"   ⚠️ {name} 下载失败: {e}")

# 启动服务
print()
print("[4/4] 配置完成！")
print()
print("=" * 50)
print("🎬 启动数字人口播服务")
print("=" * 50)
print()
print("在PowerShell中执行:")
print()
print(f"  cd {os.path.dirname(os.path.abspath(__file__))}")
print("  python server.py")
print()
print("服务启动后，打开浏览器访问:")
print("  http://localhost:5000")
print()
print("或者手机访问:")
print("  http://你电脑的IP:5000")
print()
print("📞 遇到问题联系: 微信sharing-win")
print()
