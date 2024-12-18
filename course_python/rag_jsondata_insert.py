from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import json

# 定義輸入檔案名稱
input_file = "embedding_course_info.json"

# 讀取 JSON 檔案
try:
    with open(input_file, "r", encoding="utf-8") as file:
        records = json.load(file)  # 將 JSON 文件加載為 Python 字典
except FileNotFoundError:
    print(f"檔案 {input_file} 不存在，請確認檔案名稱或路徑是否正確。")
    exit()
except json.JSONDecodeError:
    print(f"檔案 {input_file} 不是有效的 JSON 格式。")
    exit()


# 連接到 Qdrant 伺服器
qdrant = QdrantClient(url="http://localhost:6333") 


# 加載嵌入模型
encoder = SentenceTransformer("all-MiniLM-L6-v2")

# 定義集合名稱
c_name = "nsysuc_course_info"

# 如果集合不存在，則創建集合
if not qdrant.collection_exists(c_name):
    qdrant.create_collection(
        collection_name=c_name,
        vectors_config=models.VectorParams(
            size=encoder.get_sentence_embedding_dimension(),  # 向量的維度由模型定義
            distance=models.Distance.COSINE,  # 使用餘弦距離
        ),
    )

# 準備插入記錄
records_insert = []

for record in records:
    idx = record['id']            # 取得記錄 ID
    vec = record['vector']        # 取得向量數據
    doc = record['payload']       # 取得載荷 (payload)

    # 建立 Qdrant 的 Record 對象
    qdrant_record = models.Record(id=idx, vector=vec, payload=doc)
    records_insert.append(qdrant_record)

# 批量上傳記錄到 Qdrant
qdrant.upload_points(
    collection_name=c_name,
    points=records_insert,
    batch_size=128,  # 定義每批處理的記錄數量
)

print(f"成功上傳 {len(records_insert)} 條記錄到集合 {c_name}。")
