import os
import json
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
from functools import wraps

# JSON 文件路徑
DATA_DIR = "data"
USER_FILE = os.path.join(DATA_DIR, "users.json")

# 初始化資料文件夾和文件
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

app = Flask(__name__)

SECRET_KEY = "your_secret_key"

# 從 JSON 文件中加載資料
def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

# 將資料寫入 JSON 文件
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    
    # 加密密碼
    password_hash = generate_password_hash(password)
    
    # 加載使用者資料
    users = load_users()
    
    # 檢查使用者唯一性
    if username in users:
        return jsonify({"error": "Username already exists"}), 400
    
    # 插入使用者資料
    user_data = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.datetime.now().isoformat(),
        "role": "user"
    }
    users[username] = user_data
    save_users(users)
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    # 加載使用者資料
    users = load_users()
    
    # 從資料中獲取使用者資料
    user = users.get(username)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # 檢查密碼
    if not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid password"}), 401
    
    # 生成 JWT Token
    token = jwt.encode({"username": username, "role": user["role"]}, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token}), 200

@app.route('/api/user/update', methods=['PUT'])
def update_user():
    token = request.headers.get('Authorization').split(" ")[1]
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = data['username']
    email = request.json.get("email")
    role = request.json.get("role")

    # 加載使用者資料
    users = load_users()

    # 打印當前的用戶名和模擬資料庫
    print(f"Username from token: {username}")
    print(f"Current users: {users}")

    # 更新使用者資料
    if username not in users:
        return jsonify({"error": "User not found"}), 404

    if email:
        users[username]['email'] = email
    if role:
        users[username]['role'] = role

    save_users(users)
    return jsonify({"message": "User updated successfully"}), 200

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization').split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if data["role"] != role:
                return jsonify({"error": "Unauthorized access"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/admin', methods=['GET'])
@role_required("admin")
def admin_dashboard():
    return jsonify({"message": "Welcome to the admin dashboard"}), 200

if __name__ == "__main__":
    app.run(debug=True)
