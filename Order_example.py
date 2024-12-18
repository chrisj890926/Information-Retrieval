from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# 模擬課程資料
courses = [
    {"teacher": "康藝晃", "course_name": "數據分析", "time": "一(下午)", "department": "資管系", "grade": 4, "relevance_score": 0},
    {"teacher": "羅珮綺", "course_name": "深度學習", "time": "二(上午)", "department": "資管系", "grade": 3, "relevance_score": 0},
    {"teacher": "康藝晃", "course_name": "機器學習基礎", "time": "三(下午)", "department": "資管系", "grade": 4, "relevance_score": 0},
    # 更多課程...
]

def extract_keywords(query):
    """
    從使用者查詢中提取關鍵字並生成結構化的輸出。
    """
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

def calculate_relevance(course, keywords):
    """
    根據關鍵字計算課程的相關性分數。
    """
    score = 0

    # 比對教師名稱
    if "teacher" in keywords and keywords["teacher"] in course["teacher"]:
        score += 2  # 教師匹配權重較高

    # 比對上課時間
    if "time" in keywords and keywords["time"] in course["time"]:
        score += 1

    # 比對課程名稱
    if "course_name" in keywords and keywords["course_name"] in course["course_name"]:
        score += 3  # 課程名稱權重最高

    return score

@app.route('/api/parse-query', methods=['POST'])
def parse_query():
    """
    API 端點: 接收自然語言查詢並返回匹配並排序的課程列表。
    """
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    # 提取關鍵字
    keywords = extract_keywords(query)

    # 計算每門課程的相關性分數
    for course in courses:
        course["relevance_score"] = calculate_relevance(course, keywords)

    # 按相關性分數排序課程
    sorted_courses = sorted(courses, key=lambda x: x["relevance_score"], reverse=True)

    # 返回排序後的課程列表
    return jsonify({"query_keywords": keywords, "courses": sorted_courses})

if __name__ == '__main__':
    app.run(debug=True)
