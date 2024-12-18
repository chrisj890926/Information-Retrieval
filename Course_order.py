from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
import json


def match_and_sort_courses(query: str, collection_name: str = "nsysuc_course_info"):
    """
    將查詢轉換為嵌入向量，並與課程資訊進行相似度比對後排序，返回排序後的課程列表。
    
    :param query: 使用者的查詢文字
    :param collection_name: Qdrant 中的集合名稱
    :return: 排序後的課程列表 (JSON 格式)
    """
    # 初始化嵌入模型
    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    # 初始化 Qdrant 客戶端
    qdrant = QdrantClient(url="http://localhost:6333")

    # 將查詢轉換為嵌入向量
    query_vector = encoder.encode(query).tolist()

    # 在 Qdrant 中搜尋最相似的課程
    search_results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=10,  # 返回前 10 條結果
        with_payload=True,  # 包括課程的額外資訊
    )

    # 將搜尋結果轉換為 JSON 格式
    sorted_courses = [
        {
            "id": result.id,
            "score": result.score,
            "course_info": result.payload,
        }
        for result in search_results
    ]

    return sorted_courses


# 測試函式
if __name__ == "__main__":
    # 模擬使用者查詢
    user_query = "教育心理學"
    
    # 呼叫函式進行匹配和排序
    sorted_results = match_and_sort_courses(user_query)

    # 以 JSON 格式輸出結果
    print(json.dumps(sorted_results, ensure_ascii=False, indent=4))

