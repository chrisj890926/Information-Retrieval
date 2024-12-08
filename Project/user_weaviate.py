from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams, ProtocolParams
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
import datetime
from werkzeug.security import check_password_hash
import jwt
from functools import wraps

# 初始化 Weaviate 客戶端
connection_params = ConnectionParams(
    http=ProtocolParams(address="http://localhost:8080"),
    grpc=None
)
client = WeaviateClient(connection_params)

app = Flask(__name__)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    
    # 加密密碼
    password_hash = generate_password_hash(password)
    
    # 檢查使用者唯一性
    if client.query.get("User").with_where({"path": ["username"], "operator": "Equal", "valueString": username}).do()["data"]["Get"]["User"]:
        return jsonify({"error": "Username already exists"}), 400
    
    # 插入使用者資料
    user_data = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.datetime.now().isoformat(),
        "role": "user"
    }
    client.data_object.create(user_data, "User")
    return jsonify({"message": "User registered successfully!"}), 201

SECRET_KEY = "your_secret_key"

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    # 從 Weaviate 中獲取使用者資料
    user = client.query.get("User", ["username", "password_hash"]).with_where({
        "path": ["username"],
        "operator": "Equal",
        "valueString": username
    }).do()["data"]["Get"]["User"]
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # 檢查密碼
    user = user[0]
    if not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid password"}), 401
    
    # 生成 JWT Token
    token = jwt.encode({"username": username, "role": user["role"]}, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token}), 200

@app.route('/api/user/update', methods=['PUT'])
def update_user():
    token = request.headers.get('Authorization').split(" ")[1]
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = request.json.get("email")

    # 更新 Weaviate 資料
    user_id = client.query.get("User", ["id"]).with_where({"path": ["username"], "operator": "Equal", "valueString": data['username']}).do()["data"]["Get"]["User"][0]["id"]
    client.data_object.update({"email": email}, "User", user_id)

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
