import json
import os
from typing import List, Dict

from dotenv import load_dotenv
from groq import Groq

from chat_types import Message


# Load environment variables
load_dotenv()

# Message to API所需格式(dict)
def convert_messages_to_groq_format(messages: List[Message]) -> List[dict]:
    """
    Convert a Message list to Groq API message format
    """
    return [{"role": msg.role, "content": msg.content} for msg in messages]


### System Response ###
def read_system_prompt_u(file_path: str = './prompt_v5.txt') -> str:
    """
    Read system prompt from a file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        print("Warning: Prompt file not found. Using default prompt.")
        return """
        You are a course query assistant. For each course, follow these steps:
        1. Output the course code and cource name first.
        2. Write a concise course introduction in 130 characters or fewer based on the `objectives` and `description`.
        3. Provide a 70-character reason for recommending the course.
        """


def generate_response(messages: List[Message], sorted_course: str, model: str = "llama-3.1-8b-instant") -> str:
    """
    Generate a response using a language model and sorted dictionary.
    """
    # Get API Key
    api_key = os.getenv('GROQ_API_KEY')

    if not api_key or api_key == 'YOUR_GROQ_API_KEY_HERE':
        print("Warning: No valid API Key")
        return "Error: Missing API Key."

    # Read system prompt
    system_prompt = read_system_prompt_u()

    # Combined System Prompt and Courses
    combined_prompt = system_prompt.replace("<COURSES>", sorted_course)

    #print(f"{'-'*50}\nsorted_course:\n{sorted_course}\n\n")
    #print(f"{'-'*50}\nSystem_prompt + Courses:\n{combined_prompt}\n\n")

    # Initialize Groq client
    client = Groq(api_key=api_key)

    # Convert messages to Groq format
    groq_messages = convert_messages_to_groq_format(messages)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": combined_prompt},
                *groq_messages
            ],
            max_tokens=2000,
        )

        # Extract and return the response content
        return response.choices[0].message.content

    except Exception as e:
        print(f"Response generation error: {str(e)}")
        return "Error: Failed to generate response."


def test_response_generator():
    """
    Run test cases for response generation
    """
    test_case = [Message(role="user", content="我對人工智慧感興趣")]
    test_courses = "-- Course No.1 --\nID: 1603, Chinese Name: 人工智慧實務專題研討（一）, English Name: SPECIAL TOPICS IN AI PRACTICE (I), Course Code: MEME646, Objectives: 務期讓學生了解人工智慧學理及方法及學習 之必要性, Description: 系所: 機械與機電工程學系碩士班。課 程大綱: 1. 前言2. 人工智慧學理3.人工智慧方法4. 工程應用。 課程目標: 務期讓學生了解人工智慧學理及方法及學習之必要性。評分方式: 1.專題：100%。授課方式: 講授及討論, Similarity Score: 0.7467227384600597, Relevance Score: 0;\n -- Course No.2 --\nID: 295, Chinese Name: 智慧型運輸系統, English Name: INTRODUCTION TO INTELLIGENT TRANSPORTATION SYSTEMS, Course Code: GEAI1079, Objectives: 本課程旨在介紹智慧型運輸系統在基本觀念、學術研究、實務應用三方面的發展狀態，期能使修習本課程的學生能對智慧型運輸系統有基本的認識與了解，並對智慧型運輸系統在世界各先進國的發展趨勢有所掌握。, Description: 系所: 跨院選修(通)。課程大綱: 智慧型運輸系統係應用先進的資通訊 、電子、控制、機械等技術於既有的各種運輸系統之運作，以改善交通運輸問題，目的在減少交通擁擠與事故，並提昇運輸安全與效率。本課程將分成兩大部分，分別是：智慧型運輸系統的基礎建設及智慧型運輸系統的應用；前者著重於介紹智慧型運輸系統的基本觀念及構成元素，後者則是說明智慧型運輸系統在學術研究及實務應用上的發展情形。授課大綱包括：1.智慧型運輸系統之定義與內涵。2.我國智慧型運輸系統的發展歷程與組織架構演變。3.智慧型運輸系統應用技術課題說明。4.智慧型運輸系統九大子系統簡介。5.智慧型運輸系統在世界各先進國的發展情形。6.智慧型運輸系統與智慧城市。同時，本課程在疫情和緩狀況下，亦會安排現地參訪，讓修課學生更實際地瞭解智慧型運輸系統在運輸管理實務上的多元應用。。課程目標: 本課程旨在介紹智慧型運輸系統在基本觀念、學術研究、實務應用三方面的發展狀態，期能使修習本課程的學生能對智慧型運輸系統有基本的認識與了解，並對智慧型運輸系統在世界各先進國的發展趨勢有所掌握。。評分方式: 1.課堂及其他活動參與表現(道路環境條件評估與紀錄活動之參與狀況)：40%2. 期中考試：20%3.期末報告：30%4.其他超乎教師預期的傑出表現：10%。授課方式: 1.教師講授。2.專家演講與交流互動。3.現地參 訪。4.課堂討論。5.期末報告注意事項(1)為分組作業，一組人數 最多6人。(2)期末報告主題為台灣以外的各國智慧型運輸系統案例介紹與分析。(3)作業重點在於分析，不能只有介紹。(4)期末作業有被退回的可能，請認真準備與撰寫。(5)期末各組均需上台簡報 ，並繳交20頁期末報告電子檔。6.需參與道路環境條件評估與紀錄之工作，該項表現將納入學期成績評分。7.本課程有可能會配合教育創新相關研究，在不影響課程進行的狀況下進行調查與課堂紀錄。, Similarity Score: 0.6101819198847117, Relevance Score: 0;\n-- Course No.3 --\nID: 1224, Chinese Name: 智慧型運輸系統, English Name: INTRODUCTION TO INTELLIGENT TRANSPORTATION SYSTEMS, Course Code: PIS1101, Objectives: 本課程旨在介紹智慧型運輸系統在基本觀念、學術研究、實務應用三方面的發展狀態，期能使修習本課程的學生能對智慧型運輸系統有基本的認識與了解，並對智慧型運輸系統在世界各先進國的發展趨勢有所掌握。, Description: 系所: 人文暨科技跨領域學士學位學程。課程大綱: 智慧型運輸系統係 應用先進的資通訊、電子、控制、機械等技術於既有的各種運輸系統之運作，以改善交通運輸問題，目的在減少交通擁擠與事故，並提昇運輸安全與效率。本課程將分成兩大部分，分別是：智慧型運輸系統的基礎建設及智慧型運輸系統的應用；前者著重於介紹智慧型運輸系統的基本觀念及構成元素，後者則是說明智慧型運輸系統在學術研究及實務應用上的發展情形。授課大綱包括：1.智慧型運輸系統之定義與內涵。2.我國智慧型運輸系統的發展歷程與組織架構演變。3.智慧型運輸系統應用技術課題說明。4.智慧型運輸系統九大子系統簡介。5.智慧型運輸系統在世界各先進國的發展情形。6.智慧型運輸系統與智慧城市。同時，本課程在疫情和緩狀況下，亦會安排現地參訪，讓修課學生更實際地瞭解智慧型運輸系統在運輸管理實務上的多元應用。。課程目標: 本課程旨在介紹智慧型運輸系統在基本觀念、學術研究、實務應用三方面的發展狀態，期能使修習本課程的學生能對智慧型運輸系統有基本的認識與了解，並對智慧型運輸系統在世界各先進國的發展趨勢有所掌握。。評分方式: 1.課堂及其他活動參與表現(道路環境條件評估與紀錄活動之 參與狀況)：40%2.期中考試：20%3.期末報告：30%4.其他超乎教師預期的傑出表現：10%。授課方式: 1.教師講授。2.專家演講與交 流互動。3.現地參訪。4.課堂討論。5.期末報告注意事項(1)為分 組作業，一組人數最多6人。(2)期末報告主題為台灣以外的各國智慧型運輸系統案例介紹與分析。(3)作業重點在於分析，不能只有 介紹。(4)期末作業有被退回的可能，請認真準備與撰寫。(5)期末各組均需上台簡報，並繳交20頁期末報告電子檔。6.需參與道路環境條件評估與紀錄之工作，該項表現將納入學期成績評分。7.本課程有可能會配合教育創新相關研究，在不影響課程進行的狀況下進行調查與課堂紀錄。, Similarity Score: 0.5915728963618051, Relevance Score: 0;\n -- Course No.4 --\nID: 1594, Chinese Name: 智慧製造與監測技術, English Name: SMART MANUFACTURING AND MONITORING TECHNOLOGY, Course Code: MEME573, Objectives: 製造技術日新月異，搭配物聯網、感測 器、監控技術與雲端系統，智慧製造環境儼然成形。本課程為智慧製造與工業4.0的入門介紹，除了雲端與數位製造概念說明，亦包 含監控技術、感測器、APP軟體與實務範例介紹。教導學生相關理 論與應用情境，搭配APP軟體授課與實做培養學生實務經驗。, Description: 系所: 機械與機電工程學系碩士班。課程大綱: 傳授智慧製造系統與設備概念，使得修課同學習該系統的監測技術與感測器使用能力，並搭配APP軟體與無線通訊模組，實現智慧監測功能 。為了讓同學具有相關實務經驗，也安排設備應用實例與操作課程。建立同學智慧製造學理技術與實務經驗。。課程目標: 製造技術日新月異，搭配物聯網、感測器、監控技術與雲端系統，智慧製造環境儼然成形。本課程為智慧製造與工業4.0的入門介紹，除了雲 端與數位製造概念說明，亦包含監控技術、感測器、APP軟體與實 務範例介紹。教導學生相關理論與應用情境，搭配APP軟體授課與 實做培養學生實務經驗。。評分方式: 1.作業與報告：35%2.點名 ：5%3.期中考試：30%4.期末考試：30%。授課方式: 講授搭配實做, Similarity Score: 0.5890770804946021, Relevance Score: 0;\n -- Course No.5 --\nID: 900, Chinese Name: 資訊人與智慧財產權, English Name: INTELLECTUAL PROPERTY  AND INFORMATION SOCIETY, Course Code: CSE420, Objectives: 介紹知識經濟與智慧財產權之內容、趨勢及影響，並探討相關的生涯規劃以迎接挑戰。, Description: 系 所: 資訊工程學系。課程大綱: 1. 知識經濟簡介2. 智慧財產權簡介：著作權、專利權、營業秘密、商標等3. 個案探討4. 迎接知識經濟的生涯規劃。課程目標: 介紹知識經濟與智慧財產權之內容、趨勢及影響，並探討相關的生涯規劃以迎接挑戰。。評分方式: 1.出席：10%%2.平時報告、作業、考試等：50%%3.期中報告：20%%4.期末報告：20%%。授課方式: 講授、研討、出席或邀請外界人士演講若需遠距授課，其方式如下：1. 於表定上課時間連結線上課程 網址2. 學生參與遠距授課需使用攝影機及麥克風以進行互動教學, Similarity Score: 0.5886773118615175, Relevance Score: 0;"
    llm_response = generate_response(test_case, test_courses)
    print(f"\n{'-'*50}\n{llm_response}")


if __name__ == "__main__":
    test_response_generator()