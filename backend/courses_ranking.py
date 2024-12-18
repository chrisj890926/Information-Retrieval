from sentence_transformers import SentenceTransformer
import json
import re
import numpy as np

# 課程資料 JSON 檔案路徑
#COURSE_DATA_FILE = "course_info.json"
#COURSE_DATA_FILE = "combin_course_info.json"
COURSE_DATA_FILE = "embedding_course_info.json"

# 從 JSON 文件載入課程資料
def load_courses_from_file():
    try:
        with open(COURSE_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"課程資料檔案 {COURSE_DATA_FILE} 不存在，請確認路徑。")
        return []
    except json.JSONDecodeError:
        print(f"課程資料檔案 {COURSE_DATA_FILE} 格式錯誤，請檢查內容。")
        return []

# 基於向量計算相似度
def calculate_similarity(query_vector, course_vector):
    query_vec = np.array(query_vector)
    course_vec = np.array(course_vector)
    # 使用餘弦相似度進行計算
    dot_product = np.dot(query_vec, course_vec)
    norm_query = np.linalg.norm(query_vec)
    norm_course = np.linalg.norm(course_vec)
    return dot_product / (norm_query * norm_course)

# 提取關鍵字
def extract_keywords(query):
    result = {}

    # 提取授課教師
    teacher_match = re.search(r"(老師|教授|授課教師)[：:]*([\u4e00-\u9fa5]+)", query)
    if teacher_match:
        result["teacher"] = teacher_match.group(2)

    # 提取上課時間
    time_match = re.search(r"(禮拜|週)([一二三四五六日])(上午|下午|晚上|[0-9]+節)", query)
    if time_match:
        day = time_match.group(2)
        time = time_match.group(3)
        result["time"] = f"{day}({time})"

    # 提取名稱（假設名稱是簡單的詞組）
    name_match = re.search(r"(課程名稱|名稱|課)[：:]*([\u4e00-\u9fa5]+)", query)
    if name_match:
        result["course_name"] = name_match.group(2)

    return result

# 基於關鍵字提取和語義匹配的課程排序
def match_and_sort_courses(query):
    # 載入課程資料
    courses = load_courses_from_file()

    # 提取關鍵字
    keywords = extract_keywords(query)
    # keywords = query_key

    # 嵌入模型初始化
    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    # 查詢向量化
    query_vector = encoder.encode(query).tolist()

    # 計算相似度並排序
    for course in courses:
        course_vector = course["vector"]
        course["similarity_score"] = calculate_similarity(query_vector, course_vector)

        # 關鍵字匹配分數
        relevance_score = 0
        if "teacher" in keywords and keywords["teacher"] in course["payload"].get("teacher", ""):
            relevance_score += 2
        if "time" in keywords and keywords["time"] in course["payload"].get("time", ""):
            relevance_score += 1
        if "course_name" in keywords and keywords["course_name"] in course["payload"].get("chinese_name", ""):
            relevance_score += 3

        course["relevance_score"] = relevance_score

    # 按相似度和關鍵字匹配分數排序
    sorted_courses = sorted(courses, key=lambda x: (x["relevance_score"], x["similarity_score"]), reverse=True)

    # 返回排序後的結果
    return sorted_courses


# 返回前10筆資料的簡化格式
def get_top_courses(query):
    
    load_courses_from_file()

    # 排序課程
    sorted_courses = match_and_sort_courses(query)

    # 簡化輸出格式，並限制返回前10筆資料
    simplified_courses = [
        {
            "id": course["id"],
            "chinese_name": course["payload"].get("chinese_name", ""),
            "english_name": course["payload"].get("english_name", ""),
            "course_code": course["payload"].get("course_code", ""),
            "objectives": course["payload"].get("objectives", ""),
            "description": course["payload"].get("description", ""),
            "similarity_score": course["similarity_score"],
            "relevance_score": course["relevance_score"]
        }
        for course in sorted_courses[:5]
    ]

    return simplified_courses


def ranked_to_str(simplified_courses):
    num_of_course = 1
    result_str = ""
    for course in simplified_courses:
        result_str += (
            f"-- Course No.{num_of_course} --\n"
            f"ID: {course['id']}, "
            f"Chinese Name: {course['chinese_name']}, "
            f"English Name: {course['english_name']}, "
            f"Course Code: {course['course_code']}, "
            f"Objectives: {course['objectives']}, "
            f"Description: {course['description']}, "
            f"Similarity Score: {course['similarity_score']}, "
            f"Relevance Score: {course['relevance_score']};\n\n"
        )
        num_of_course += 1
    return result_str


if __name__ == "__main__":
    query = "名稱: 人工智慧"
    top_courses = ranked_to_str(get_top_courses(query))
    print(top_courses, type(top_courses))
    # print("-"*50)