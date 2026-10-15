from flask import Flask, request, jsonify, render_template_string
import hashlib
import time
import os

app = Flask(__name__)

# ==================== CẤU HÌNH ====================
ADMIN_PASSWORD = "hoang123"          # Đổi mật khẩu này
DEFAULT_HOURS = 24
# ==================================================

keys = {}

def generate_key():
    raw = f"{time.time()}{os.urandom(8).hex()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12].upper()

@app.route("/")
def home():
    return "Server key đang chạy"

# Trang admin tạo key thủ công
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password != ADMIN_PASSWORD:
            return "Sai mật khẩu"

        hours = int(request.form.get("hours", DEFAULT_HOURS))
        key = generate_key()
        expire = int(time.time()) + hours * 3600
        keys[key] = {"expire": expire, "hours": hours}

        return f"""
        <h2>Đã tạo key thành công</h2>
        <h1 style="color:red">{key}</h1>
        <p>Thời hạn: {hours} giờ</p>
        <a href="/admin">Tạo key khác</a>
        """

    return '''
    <form method="post">
        <h2>Tạo key thủ công</h2>
        Mật khẩu admin: <input type="password" name="password"><br><br>
        Thời hạn (giờ): <input type="number" name="hours" value="24" min="1"><br><br>
        <button type="submit">Tạo key</button>
    </form>
    '''

# Kiểm tra key (bot gọi vào đây)
@app.route("/check-key")
def check_key():
    key = request.args.get("key")
    if not key:
        return jsonify({"valid": False, "message": "Thiếu key"})

    info = keys.get(key)
    if info and info["expire"] > time.time():
        remaining = int((info["expire"] - time.time()) / 3600)
        return jsonify({"valid": True, "remaining_hours": remaining})
    
    return jsonify({"valid": False, "message": "Key sai hoặc hết hạn"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
