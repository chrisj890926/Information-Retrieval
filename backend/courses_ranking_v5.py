from sentence_transformers import SentenceTransformer
import json
import numpy as np
import re

# 課程資料 JSON 檔案路徑
COURSE_DATA_FILE = "embedding_course_info.json"

# 從 JSON 文件載入課程資料
def load_courses_from_file():
    try:
        with open(COURSE_DATA_FILE, "r", encoding="utf-8") as file:
            courses = json.load(file)
            valid_courses = [course for course in courses if "vector" in course and "payload" in course]
            if not valid_courses:
                raise ValueError("課程資料缺少必要的向量資訊或 payload。")
            return valid_courses
    except FileNotFoundError:
        raise FileNotFoundError(f"課程資料檔案 {COURSE_DATA_FILE} 不存在，請確認路徑。")
    except json.JSONDecodeError:
        raise ValueError(f"課程資料檔案 {COURSE_DATA_FILE} 格式錯誤，請檢查內容。")

# 查詢嵌入向量計算
def get_query_vector(query, model_name="all-MiniLM-L6-v2"):
    encoder = SentenceTransformer(model_name)
    return encoder.encode(query).tolist()

# 基於向量計算相似度
def calculate_similarity(query_vector, course_vector):
    dot_product = np.dot(query_vector, course_vector)
    norm_query = np.linalg.norm(query_vector)
    norm_course = np.linalg.norm(course_vector)
    return dot_product / (norm_query * norm_course) if norm_query and norm_course else 0.0

# 基於語義匹配的課程排序
# 管道1：課程資訊與系所
# 管道2：其他資訊
def match_and_sort_courses(query, model_name="all-MiniLM-L6-v2"):
    courses = load_courses_from_file()
    query_vector = get_query_vector(query, model_name)

    for course in courses:
        # 管道1：課程資訊與系所相似度計算
        info_fields = ["chinese_name", "course_code", "department"]
        info_text = " ".join([course["payload"].get(field, "") for field in info_fields])
        info_vector = get_query_vector(info_text, model_name)
        info_similarity = calculate_similarity(query_vector, info_vector)

        # 管道2：其他資訊相似度計算
        other_fields = ["objectives", "description"]
        other_text = " ".join([course["payload"].get(field, "") for field in other_fields])
        other_vector = get_query_vector(other_text, model_name)
        other_similarity = calculate_similarity(query_vector, other_vector)

        # 綜合相似度計算
        course["similarity_score"] = 0.6 * info_similarity + 0.4 * other_similarity

    sorted_courses = sorted(courses, key=lambda x: x["similarity_score"], reverse=True)
    return sorted_courses

# 返回前10筆資料的簡化格式
def get_top_courses(query, top_k=10):
    sorted_courses = match_and_sort_courses(query)
    simplified_courses = [
        {
            "id": course["id"],
            "chinese_name": course["payload"].get("chinese_name", ""),
            "english_name": course["payload"].get("english_name", ""),
            "course_code": course["payload"].get("course_code", ""),
            "objectives": course["payload"].get("objectives", ""),
            "description": course["payload"].get("description", ""),
            "similarity_score": course["similarity_score"]
        }
        for course in sorted_courses[:top_k]
    ]
    return simplified_courses

# 課程排序輸出格式化
def ranked_to_str(simplified_courses):
    result_str = ""
    for idx, course in enumerate(simplified_courses, start=1):
        result_str += (
            f"-- Course No.{idx}\n"
            f"ID: {course['id']}, "
            f"Chinese Name: {course['chinese_name']}, "
            f"English Name: {course['english_name']}, "
            f"Course Code: {course['course_code']}, "
            f"Objectives: {course['objectives']}, "
            f"Description: {course['description']}, "
            f"Similarity Score: {course['similarity_score']:.4f};\n\n"
        )
    return result_str

if __name__ == "__main__":
    query = "授課方式: 線上, 名稱: 資訊管理, 系所: 資管系"
    top_courses = ranked_to_str(get_top_courses(query))
    print(top_courses)
