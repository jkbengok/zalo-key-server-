from flask import Flask, request, jsonify
import hashlib
import time
import os
import requests

app = Flask(__name__)

# ==================== CẤU HÌNH ====================
LINK4M_API_KEY = "683722d2cb3cec434a49f527"
SECRET = "mot_chuoi_bi_mat_cua_ban"          # Đổi thành chuỗi bất kỳ của bạn
KEY_EXPIRE_HOURS = 24                        # Key sống bao nhiêu giờ
# ==================================================

keys = {}

def generate_key(user_id=""):
    raw = f"{user_id}{SECRET}{int(time.time())}"
    return hashlib.md5(raw.encode()).hexdigest()[:12].upper()

@app.route("/")
def home():
    return "Server key đang chạy"

# Tạo link lấy key
@app.route("/get-link", methods=["GET"])
def get_link():
    user_id = request.args.get("uid", "guest")
    key = generate_key(user_id)
    expire = int(time.time()) + KEY_EXPIRE_HOURS * 3600
    keys[key] = {"expire": expire, "uid": user_id}

    # Link đích sẽ hiện key
    target = request.host_url.rstrip("/") + f"/show-key?key={key}"
    
    try:
        r = requests.get(
            "https://link4m.co/st",
            params={"api": LINK4M_API_KEY, "url": target},
            timeout=10
        )
        data = r.json()
        short = data.get("shortenedUrl") or data.get("url") or target
    except Exception as e:
        short = target
        print("Lỗi tạo link4m:", e)

    return jsonify({
        "status": "success",
        "key": key,
        "link": short,
        "expire_hours": KEY_EXPIRE_HOURS
    })

# Trang hiện key sau khi vượt link4m
@app.route("/show-key")
def show_key():
    key = request.args.get("key")
    if key in keys and keys[key]["expire"] > time.time():
        return f"""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>Key của bạn:</h2>
            <h1 style="color: #e74c3c;">{key}</h1>
            <p>Hết hạn sau {KEY_EXPIRE_HOURS} giờ</p>
            <p>Copy key này rồi dán vào bot</p>
        </body>
        </html>
        """
    return "<h3>Key không hợp lệ hoặc đã hết hạn</h3>"

# Bot gọi vào đây để kiểm tra key
@app.route("/check-key", methods=["GET", "POST"])
def check_key():
    key = request.args.get("key")
    if request.is_json:
        key = request.json.get("key") or key

    if not key:
        return jsonify({"valid": False, "message": "Thiếu key"})

    info = keys.get(key)
    if info and info["expire"] > time.time():
        return jsonify({"valid": True, "message": "Key hợp lệ"})
    
    return jsonify({"valid": False, "message": "Key sai hoặc đã hết hạn"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)